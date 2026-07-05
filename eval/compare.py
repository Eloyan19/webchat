#!/usr/bin/env python3
"""Grounding & citation eval for the webchat RAG control question set.

For each in-domain question it calls the backend /chat in cited mode
(useRag=true, improvedRag=true) and checks the anti-hallucination contract:
  - sources present in the answer,
  - a verbatim quote present for every source (the backend already validates
    each quote is a real substring of its chunk; here we confirm non-emptiness),
  - the answer is grounded in those quotes — scored by a DeepSeek LLM judge,
  - (retrieval hit) the expected source file was actually retrieved.

For each off-topic question it checks that the assistant abstains ("не знаю")
instead of answering from the model's own knowledge (ragMeta.abstained == true).

Writes results.json and REPORT.md.

Runs against the backend directly (127.0.0.1:8000) on purpose: that bypasses the
nginx token gate and rate limit. Override with BACKEND_URL / CHAT_TOKEN env vars.
"""
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CHAT_TOKEN = os.getenv("CHAT_TOKEN", "")
HERE = Path(__file__).parent


def ask(messages: list[dict], use_rag: bool, improved: bool) -> dict:
    body = json.dumps({
        "messages": messages,
        "useRag": use_rag, "improvedRag": improved,
    }).encode()
    headers = {"Content-Type": "application/json"}
    if CHAT_TOKEN:
        headers["Authorization"] = f"Bearer {CHAT_TOKEN}"
    req = urllib.request.Request(f"{BACKEND_URL}/chat", data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def hit(expected: list[str], sources: list[dict]) -> bool:
    files = [s["file"] for s in sources]
    return any(exp in files for exp in expected)


def judge(question: str, answer: str, quotes: list[str]) -> tuple[bool | None, str]:
    """LLM judge (DeepSeek via backend, no RAG): does the answer follow from the
    quotes? Returns (grounded|None, reason); None if it can't be scored."""
    if not quotes:
        return None, "нет цитат для проверки"
    quoted = "\n".join(f"[{i}] {q}" for i, q in enumerate(quotes, 1))
    prompt = (
        "Ты — строгий проверяющий фактической опоры ответа на цитаты. Дан вопрос, "
        "ответ ассистента и цитаты из источников, на которые он опирался. Реши, "
        "следует ли фактическое содержание ответа из этих цитат (подтверждается ими, "
        "не выдумано и не противоречит им). Язык ответа и цитат может отличаться — "
        "оценивай смысл, а не язык.\n"
        'Ответь СТРОГО одним JSON-объектом: {"grounded": true|false, "reason": "<кратко по-русски>"}.\n\n'
        f"Вопрос: {question}\n\nОтвет ассистента: {answer}\n\nЦитаты:\n{quoted}"
    )
    try:
        reply = ask([{"role": "user", "content": prompt}], False, False)["reply"]
        m = re.search(r"\{.*\}", reply, re.S)
        data = json.loads(m.group(0)) if m else {}
        return bool(data.get("grounded")), str(data.get("reason", "")).strip()
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, ValueError) as e:
        return None, f"ошибка судьи: {e}"


def run_indomain(q: dict) -> dict:
    messages = q.get("context", []) + [{"role": "user", "content": q["question"]}]
    r = ask(messages, True, True)  # cited mode: sources + quotes + threshold gate
    sources = r.get("sources", [])
    meta = r.get("ragMeta", {})
    quotes = [s["quote"] for s in sources if s.get("quote")]
    abstained = bool(meta.get("abstained"))
    checks = {
        "sources_present": len(sources) > 0,
        "quotes_present": len(sources) > 0 and len(quotes) == len(sources),
        "quotes_dropped": meta.get("quotesDropped", 0),
        "abstained": abstained,
        "retrieval_hit": hit(q["expected_sources"], sources),
    }
    if abstained:
        grounded, reason = None, "ассистент воздержался (не знаю)"
    else:
        grounded, reason = judge(q["question"], r["reply"], quotes)
    return {
        **q, "type": "indomain",
        "reply": r["reply"],
        "rewritten_query": r.get("rewrittenQuery"),
        "sources": [{"file": s["file"], "section": s["section"],
                     "quote": s.get("quote")} for s in sources],
        "checks": checks, "grounded": grounded, "grounded_reason": reason,
    }


def run_offtopic(q: dict) -> dict:
    r = ask([{"role": "user", "content": q["question"]}], True, True)
    meta = r.get("ragMeta", {})
    abstained = bool(meta.get("abstained"))
    return {
        **q, "type": "offtopic",
        "reply": r["reply"], "abstained": abstained,
        "pass": abstained, "sources": r.get("sources", []),
    }


def main() -> None:
    questions = json.loads((HERE / "questions.json").read_text())
    indomain = [q for q in questions if not q.get("offtopic")]
    offtopic = [q for q in questions if q.get("offtopic")]
    results = []

    for q in indomain:
        turns = "  (multi-turn)" if q.get("context") else ""
        print(f"[in {q['id']:2d}] {q['question'][:56]}...{turns}")
        results.append(run_indomain(q))
        time.sleep(0.3)

    for q in offtopic:
        print(f"[off {q['id']:2d}] {q['question'][:56]}...")
        results.append(run_offtopic(q))
        time.sleep(0.3)

    (HERE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
    write_report(results)

    ind = [r for r in results if r["type"] == "indomain"]
    off = [r for r in results if r["type"] == "offtopic"]
    n = len(ind)
    sp = sum(r["checks"]["sources_present"] for r in ind)
    qp = sum(r["checks"]["quotes_present"] for r in ind)
    gr = sum(r["grounded"] is True for r in ind)
    ab = sum(r["pass"] for r in off)
    print(f"\nDone. In-domain: источники {sp}/{n} · цитаты {qp}/{n} · grounded {gr}/{n}. "
          f"Off-topic abstain: {ab}/{len(off)}. See eval/REPORT.md")


def q_block(text: str) -> str:
    return "> " + text.replace("\n", "\n> ")


def _mark(ok: bool) -> str:
    return "✅" if ok else "❌"


def write_report(results: list[dict]) -> None:
    ind = [r for r in results if r["type"] == "indomain"]
    off = [r for r in results if r["type"] == "offtopic"]
    n = len(ind)
    sp = sum(r["checks"]["sources_present"] for r in ind)
    qp = sum(r["checks"]["quotes_present"] for r in ind)
    gr = sum(r["grounded"] is True for r in ind)
    ab = sum(r["pass"] for r in off)

    lines = [
        "# Цитаты, источники и режим «не знаю» — отчёт eval",
        "",
        "Генерируется `compare.py`. Корпус — Google *compose-samples*. Прогон в "
        "**cited-режиме** (`useRag=true, improvedRag=true`): извлечение → порог-фильтр → "
        "генерация со структурированными цитатами. Цитаты валидируются backend как "
        "дословные подстроки чанков; здесь судья DeepSeek проверяет, следует ли смысл "
        "ответа из этих цитат.",
        "",
        "## Сводка",
        "",
        f"- **Источники в ответе:** {sp}/{n}",
        f"- **Цитаты в ответе:** {qp}/{n}",
        f"- **Ответ обоснован цитатами (судья):** {gr}/{n}",
        f"- **Off-topic → «не знаю» (abstain):** {ab}/{len(off)}",
        "",
        "## In-domain",
        "",
        "| # | Вопрос | Источники | Цитаты | Обоснован | Retrieval hit |",
        "|---|--------|:---:|:---:|:---:|:---:|",
    ]
    for r in ind:
        c = r["checks"]
        marker = "🔁 " if r.get("context") else ""
        grounded = "—" if r["grounded"] is None else _mark(r["grounded"])
        lines.append(
            f"| {r['id']} | {marker}{r['question'][:46]}… | {_mark(c['sources_present'])} | "
            f"{_mark(c['quotes_present'])} | {grounded} | {_mark(c['retrieval_hit'])} |"
        )
    lines += [
        "",
        "## Off-topic (проверка режима «не знаю»)",
        "",
        "| # | Вопрос | Abstain «не знаю»? |",
        "|---|--------|:---:|",
    ]
    for r in off:
        lines.append(f"| {r['id']} | {r['question'][:52]}… | {_mark(r['pass'])} |")
    lines += ["", "---", ""]

    for r in ind:
        c = r["checks"]
        lines += [f"## {r['id']}. {r['question']}", ""]
        if r.get("context"):
            convo = "\n".join(f"{m['role']}: {m['content']}" for m in r["context"])
            lines += ["**Контекст диалога (multi-turn):**", "", q_block(convo), ""]
        grounded = "—" if r["grounded"] is None else _mark(r["grounded"])
        lines += [
            f"**Ожидание:** {r['expectation']}",
            "",
            f"**Проверки:** источники {_mark(c['sources_present'])} · "
            f"цитаты {_mark(c['quotes_present'])} · отброшено цитат {c['quotes_dropped']} · "
            f"обоснован {grounded} · retrieval hit {_mark(c['retrieval_hit'])}",
            "",
            f"**Судья:** {r['grounded_reason']}",
            "",
            "**Ответ:**", "", q_block(r["reply"]), "",
            "**Источники и цитаты:**", "",
        ]
        if r["sources"]:
            for i, s in enumerate(r["sources"], 1):
                lines.append(f"{i}. `{s['file']}` :: {s['section']}")
                if s.get("quote"):
                    lines += ["", q_block(s["quote"]), ""]
        else:
            lines += ["_нет_", ""]
        lines += ["---", ""]

    lines += ["## Off-topic — ответы", ""]
    for r in off:
        lines += [
            f"### {r['id']}. {r['question']}",
            "",
            f"**Abstain:** {_mark(r['pass'])}",
            "",
            q_block(r["reply"]), "",
        ]

    (HERE / "REPORT.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()

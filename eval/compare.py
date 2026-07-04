#!/usr/bin/env python3
"""RAG mode comparison harness for the webchat control question set.

For each question in questions.json it calls the backend /chat in three modes:
  - no_rag:       useRag=false                  (model's own knowledge)
  - plain_rag:    useRag=true, improvedRag=false (single-stage top-k retrieval)
  - improved_rag: useRag=true, improvedRag=true  (query rewrite + threshold filter
                  + rerank, k_before -> k_after)
It records each answer, the sources RAG used, the rewritten query, and whether the
expected source file was retrieved (retrieval hit) for plain vs improved. Writes
results.json and a side-by-side REPORT.md.

Runs against the backend directly (127.0.0.1:8000) on purpose: that bypasses the
nginx token gate and rate limit, so the burst of requests doesn't trip HTTP 429.
Override with BACKEND_URL / CHAT_TOKEN env vars to point at the public URL.
"""
import json
import os
import time
import urllib.request
from pathlib import Path

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CHAT_TOKEN = os.getenv("CHAT_TOKEN", "")
HERE = Path(__file__).parent


def ask(question: str, use_rag: bool, improved: bool) -> dict:
    body = json.dumps({
        "messages": [{"role": "user", "content": question}],
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


def main() -> None:
    questions = json.loads((HERE / "questions.json").read_text())
    results = []
    for q in questions:
        print(f"[{q['id']:2d}/{len(questions)}] {q['question'][:66]}...")
        no_rag = ask(q["question"], False, False)
        plain = ask(q["question"], True, False)
        improved = ask(q["question"], True, True)
        results.append({
            **q,
            "no_rag": {"reply": no_rag["reply"]},
            "plain_rag": {
                "reply": plain["reply"],
                "sources": [s["file"] for s in plain.get("sources", [])],
                "hit": hit(q["expected_sources"], plain.get("sources", [])),
            },
            "improved_rag": {
                "reply": improved["reply"],
                "sources": [s["file"] for s in improved.get("sources", [])],
                "hit": hit(q["expected_sources"], improved.get("sources", [])),
                "rewritten_query": improved.get("rewrittenQuery"),
                "rag_meta": improved.get("ragMeta", {}),
            },
        })
        time.sleep(0.3)

    (HERE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
    write_report(results)
    ph = sum(r["plain_rag"]["hit"] for r in results)
    ih = sum(r["improved_rag"]["hit"] for r in results)
    print(f"\nDone. Retrieval hits — plain: {ph}/{len(results)}, improved: {ih}/{len(results)}."
          f" See eval/REPORT.md")


def q(text: str) -> str:
    return "> " + text.replace("\n", "\n> ")


def write_report(results: list[dict]) -> None:
    ph = sum(r["plain_rag"]["hit"] for r in results)
    ih = sum(r["improved_rag"]["hit"] for r in results)
    lines = [
        "# Сравнение режимов RAG: no-RAG / plain / improved",
        "",
        "Генерируется `compare.py`. Корпус — Google *compose-samples*. Генерацию делает "
        "DeepSeek; RAG добавляет извлечённые чанки как system-контекст.",
        "",
        "**Режимы:** `no-RAG` (знания модели) · `plain` (top-k retrieval) · "
        "`improved` (query rewrite + порог-фильтр + rerank, k_before→k_after).",
        "",
        "## Сводка",
        "",
        "| # | Вопрос | plain: источник извлечён? | improved: источник извлечён? |",
        "|---|--------|:---:|:---:|",
    ]
    for r in results:
        lines.append(
            f"| {r['id']} | {r['question'][:52]}… | "
            f"{'✅' if r['plain_rag']['hit'] else '❌'} | "
            f"{'✅' if r['improved_rag']['hit'] else '❌'} |"
        )
    lines += [
        "",
        f"**Retrieval hit rate:** plain {ph}/{len(results)} · improved {ih}/{len(results)} "
        "(на уровне файла).",
        "",
        "> `improved` = query rewrite (только для multi-turn) + фильтр по cross-encoder "
        "`rerank_score` + rerank-порядок из сервиса `../rag/`. Реранкер переупорядочивает "
        "кандидатов по релевантности, поэтому нужный чанк чаще попадает в топ-K.",
        "",
        "---",
        "",
    ]
    for r in results:
        imp = r["improved_rag"]
        lines += [
            f"## {r['id']}. {r['question']}",
            "",
            f"**Ожидание:** {r['expectation']}",
            "",
            f"**Ожидаемые источники:** {', '.join(f'`{s}`' for s in r['expected_sources'])}",
            "",
            f"**Переписанный запрос (improved):** `{imp['rewritten_query']}`",
            "",
            f"**Retrieval hit:** plain {'✅' if r['plain_rag']['hit'] else '❌'} · "
            f"improved {'✅' if imp['hit'] else '❌'} · "
            f"фильтр improved: {imp['rag_meta'].get('k_returned', '?')} → "
            f"{imp['rag_meta'].get('k_after_filter', '?')} "
            f"(порог {imp['rag_meta'].get('threshold', '?')})",
            "",
            "**no-RAG:**", "", q(r["no_rag"]["reply"]), "",
            "**plain RAG:**", "", q(r["plain_rag"]["reply"]), "",
            f"_источники:_ {', '.join(f'`{s}`' for s in r['plain_rag']['sources']) or '—'}", "",
            "**improved RAG:**", "", q(imp["reply"]), "",
            f"_источники:_ {', '.join(f'`{s}`' for s in imp['sources']) or '—'}", "",
            "---", "",
        ]
    (HERE / "REPORT.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()

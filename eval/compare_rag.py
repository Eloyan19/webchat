#!/usr/bin/env python3
"""Сравнение режимов RAG: no-RAG · plain · improved (Задания 2 и 3).

Для каждого контрольного вопроса гоняет backend /chat в ТРЁХ режимах и сравнивает:
  - no-RAG   (useRag=false)               — ответ из знаний модели, без источников;
  - plain    (useRag=true, improved=false) — одностадийный top-k retrieval;
  - improved (useRag=true, improved=true)  — query rewrite + rerank + порог-фильтр.

Метрика — детерминированная, без LLM-судьи: retrieval_hit (на уровне файла) —
попал ли хоть один ожидаемый файл (expected_sources) в источники ответа. У no-RAG
источников нет по определению — его колонка показывает сам ответ (для контраста).

Показывает две вещи из задания:
  • Задание 2 — no-RAG vs RAG: без RAG модель отвечает из общих знаний (часто
    уверенно неверно), с RAG — по источнику либо честно «не знаю».
  • Задание 3 — plain vs improved: rerank + rewrite поднимают hit-rate
    (обычно plain < improved, отрыв дают multi-turn вопросы за счёт rewrite).

Пишет REPORT-modes.md и печатает сводку. Бьёт НАПРЯМУЮ в backend (127.0.0.1:8000),
минуя nginx-гейт и rate-limit. Override: BACKEND_URL / CHAT_TOKEN.

Запуск (из каталога eval/, backend и rag-сервис подняты):  python3 compare_rag.py
"""
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CHAT_TOKEN = os.getenv("CHAT_TOKEN", "")
HERE = Path(__file__).parent

# (метка, useRag, improvedRag)
MODES = [("no-RAG", False, False), ("plain", True, False), ("improved", True, True)]


def ask(messages: list[dict], use_rag: bool, improved: bool) -> dict:
    body = json.dumps({
        "messages": messages, "useRag": use_rag, "improvedRag": improved,
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


def run_question(q: dict) -> dict:
    ctx = q.get("context", [])
    row = {
        "id": q["id"], "question": q["question"], "expectation": q["expectation"],
        "expected_sources": q["expected_sources"], "multiturn": bool(ctx), "modes": {},
    }
    for name, use_rag, improved in MODES:
        messages = ctx + [{"role": "user", "content": q["question"]}]
        r = ask(messages, use_rag, improved)
        sources = r.get("sources", [])
        meta = r.get("ragMeta", {})
        row["modes"][name] = {
            "reply": r.get("reply", ""),
            "sources": [s["file"] for s in sources],
            "hit": hit(q["expected_sources"], sources) if use_rag else None,
            "abstained": bool(meta.get("abstained")),
            "rewritten": r.get("rewrittenQuery"),
        }
        time.sleep(0.3)
    return row


def _mark(v) -> str:
    if v is None:
        return "—"
    return "✅" if v else "❌"


def write_report(rows: list[dict]) -> None:
    n = len(rows)
    hit_plain = sum(r["modes"]["plain"]["hit"] for r in rows)
    hit_impr = sum(r["modes"]["improved"]["hit"] for r in rows)

    L = [
        "# Сравнение режимов RAG — no-RAG · plain · improved",
        "",
        "Генерируется `compare_rag.py`. Корпус — Google *compose-samples*. Каждый "
        "контрольный вопрос прогнан в трёх режимах против backend `/chat`.",
        "",
        "**Метрика — retrieval hit (уровень файла):** попал ли ожидаемый файл "
        "(`expected_sources`) в источники ответа. У no-RAG источников нет — показан "
        "сам ответ (из знаний модели).",
        "",
        "## Сводка",
        "",
        f"- **plain** (одностадийный retrieval): hit **{hit_plain}/{n}**",
        f"- **improved** (rewrite + rerank + порог): hit **{hit_impr}/{n}**",
        f"- Отрыв improved над plain: **+{hit_impr - hit_plain}** "
        "(обычно за счёт multi-turn вопросов, где помогает query rewrite).",
        "",
        "| # | Вопрос | plain hit | improved hit |",
        "|---|--------|:---:|:---:|",
    ]
    for r in rows:
        mt = "🔁 " if r["multiturn"] else ""
        L.append(
            f"| {r['id']} | {mt}{r['question'][:50]}… | "
            f"{_mark(r['modes']['plain']['hit'])} | {_mark(r['modes']['improved']['hit'])} |"
        )
    L += ["", "---", "", "## По вопросам (ответ каждого режима)", ""]
    for r in rows:
        L += [f"### {r['id']}. {r['question']}", ""]
        if r["multiturn"]:
            L.append("_multi-turn: вопрос ссылается на предыдущие реплики диалога._\n")
        L.append(f"**Ожидание:** {r['expectation']}")
        L.append(f"\n**Ожидаемый источник:** `{', '.join(r['expected_sources'])}`\n")
        for name, _, _ in MODES:
            m = r["modes"][name]
            reply = " ".join(m["reply"].split())
            reply = reply[:300] + ("…" if len(reply) > 300 else "")
            head = f"**{name}**"
            if m["hit"] is not None:
                head += f" · retrieval hit {_mark(m['hit'])}"
            if name == "improved" and m.get("rewritten"):
                head += f" · переписанный запрос: _{m['rewritten']}_"
            L += [head, "", f"> {reply}"]
            if m["sources"]:
                L.append(f"> \n> _источники: {', '.join(m['sources'])}_")
            L.append("")
        L += ["---", ""]

    (HERE / "REPORT-modes.md").write_text("\n".join(L), encoding="utf-8")


def main() -> None:
    questions = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    indomain = [q for q in questions if not q.get("offtopic")]
    rows = []
    for q in indomain:
        mt = "  (multi-turn)" if q.get("context") else ""
        print(f"[{q['id']:2d}] {q['question'][:56]}...{mt}")
        rows.append(run_question(q))

    write_report(rows)

    n = len(rows)
    hp = sum(r["modes"]["plain"]["hit"] for r in rows)
    hi = sum(r["modes"]["improved"]["hit"] for r in rows)
    print(f"\nDone. retrieval hit — plain {hp}/{n} · improved {hi}/{n} "
          f"(отрыв +{hi - hp}). См. eval/REPORT-modes.md")


if __name__ == "__main__":
    main()

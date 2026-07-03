#!/usr/bin/env python3
"""RAG vs no-RAG comparison harness for the webchat control question set.

For each question in questions.json it calls the backend /chat twice — once with
useRag=false and once with useRag=true — and records both answers plus the
sources RAG retrieved. It then checks whether the expected source file was among
the retrieved chunks (retrieval hit) and writes a side-by-side REPORT.md.

Runs against the backend directly (127.0.0.1:8000) on purpose: that bypasses the
nginx token gate and rate limit, so 20 rapid requests don't trip HTTP 429.
Override with BACKEND_URL / CHAT_TOKEN env vars if you point it at the public URL.
"""
import json
import os
import time
import urllib.request
from pathlib import Path

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CHAT_TOKEN = os.getenv("CHAT_TOKEN", "")
HERE = Path(__file__).parent


def ask(use_rag: bool, question: str) -> tuple[str, list[str]]:
    body = json.dumps({"useRag": use_rag, "messages": [{"role": "user", "content": question}]}).encode()
    headers = {"Content-Type": "application/json"}
    if CHAT_TOKEN:
        headers["Authorization"] = f"Bearer {CHAT_TOKEN}"
    req = urllib.request.Request(f"{BACKEND_URL}/chat", data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.load(resp)
    return data["reply"], [s["file"] for s in data.get("sources", [])]


def retrieval_hit(expected: list[str], retrieved: list[str]) -> bool:
    return any(exp in retrieved for exp in expected)


def main() -> None:
    questions = json.loads((HERE / "questions.json").read_text())
    results = []
    for q in questions:
        print(f"[{q['id']:2d}/{len(questions)}] {q['question'][:70]}...")
        reply_off, _ = ask(False, q["question"])
        reply_on, sources = ask(True, q["question"])
        hit = retrieval_hit(q["expected_sources"], sources)
        results.append({**q, "reply_no_rag": reply_off, "reply_rag": reply_on,
                        "rag_sources": sources, "retrieval_hit": hit})
        time.sleep(0.3)

    (HERE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
    write_report(results)
    hits = sum(r["retrieval_hit"] for r in results)
    print(f"\nDone. Retrieval hits: {hits}/{len(results)}. See eval/REPORT.md")


def write_report(results: list[dict]) -> None:
    lines = [
        "# RAG vs no-RAG — сравнение качества",
        "",
        "Генерируется `compare.py`. Корпус — Google *compose-samples* (Jetchat, JetNews, "
        "Reply, Jetsnack, Jetcaster, JetLagged). Генерацию делает DeepSeek; RAG добавляет "
        "извлечённые чанки как system-контекст.",
        "",
        "**Как читать:** вопросы код-специфичные. Без RAG модель обычно выдаёт "
        "правдоподобный, но неверный код/пути (галлюцинация); с RAG — отвечает по "
        "источникам либо честно говорит, что в контексте нет.",
        "",
        "## Сводка",
        "",
        "| # | Вопрос | Ожидаемый источник извлечён? |",
        "|---|--------|:---:|",
    ]
    for r in results:
        hit = "✅" if r["retrieval_hit"] else "❌"
        lines.append(f"| {r['id']} | {r['question'][:60]}… | {hit} |")
    hits = sum(r["retrieval_hit"] for r in results)
    lines += [
        "",
        f"**Retrieval hit rate:** {hits}/{len(results)} "
        f"(доля вопросов, где нужный файл попал в извлечённые чанки).",
        "",
        "---",
        "",
    ]
    for r in results:
        hit = "✅ да" if r["retrieval_hit"] else "❌ нет"
        lines += [
            f"## {r['id']}. {r['question']}",
            "",
            f"**Ожидание:** {r['expectation']}",
            "",
            f"**Ожидаемые источники:** {', '.join(f'`{s}`' for s in r['expected_sources'])}",
            "",
            f"**Нужный источник извлечён:** {hit}",
            "",
            "**Ответ БЕЗ RAG:**",
            "",
            "> " + r["reply_no_rag"].replace("\n", "\n> "),
            "",
            "**Ответ С RAG:**",
            "",
            "> " + r["reply_rag"].replace("\n", "\n> "),
            "",
            f"**Источники RAG:** {', '.join(f'`{s}`' for s in r['rag_sources']) or '—'}",
            "",
            "---",
            "",
        ]
    (HERE / "REPORT.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()

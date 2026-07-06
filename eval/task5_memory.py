#!/usr/bin/env python3
"""QA Задания 5 — «память задачи» + источники каждый ход.

Два многоходовых сценария (по ~7 пользовательских реплик = 14 сообщений) гоняются
через задеплоенный backend НАПРЯМУЮ (http://127.0.0.1:8000, минуя nginx-гейт/лимит),
каждый — со своим постоянным sessionId. Проверяем два инварианта Задания 5:

  1) task_state.goal НЕ теряется по ходу диалога (единожды установлен — держится);
  2) у каждого НЕ-abstain RAG-ответа есть источники (grounding не регрессировал).

Запуск (backend + rag-search должны быть подняты):
    .venv/bin/python eval/task5_memory.py
Пишет краткий отчёт в eval/REPORT-task5.md и выходит с кодом 1 при провале assert'ов.
"""

import json
import sys
import uuid
from pathlib import Path

import httpx

BACKEND = "http://127.0.0.1:8000/chat"
REPORT = Path(__file__).with_name("REPORT-task5.md")

# Сценарии: список пользовательских реплик. Держимся тем, реально извлекаемых из
# корпуса compose-samples (Jetchat / JetNews), чтобы RAG не уходил в abstain.
SCENARIOS = [
    {
        "name": "Jetchat: управление состоянием беседы",
        "turns": [
            "In Jetchat, which class holds the conversation UI state? I'm studying how messages are stored.",
            "What constructor parameters does that ConversationUiState class take?",
            "At which position does its addMessage() insert a new message?",
            "What fields does the Message data class have?",
            "How is the message list backed so Compose observes changes?",
            "Which UI tests cover the conversation screen in the androidTest suite?",
            "Summarize what I've learned about Jetchat's conversation state so far.",
        ],
    },
    {
        "name": "JetNews: UI-state и обработка ошибок",
        "turns": [
            "In JetNews, I want to understand the home screen UI state. What type is HomeUiState?",
            "Which three common properties does that sealed interface declare?",
            "What fields does the ErrorMessage data class contain?",
            "How does HomeViewModel expose the UI state to the composables?",
            "How are error messages surfaced to the user in JetNews?",
            "What are the two subtypes of the HomeUiState sealed interface?",
            "Recap the JetNews home-state design we've discussed.",
        ],
    },
]


def run_scenario(scenario: dict) -> dict:
    session_id = f"qa-task5-{uuid.uuid4()}"
    messages: list[dict] = []
    turns_log: list[dict] = []
    goals_seen: list[str] = []

    for user_text in scenario["turns"]:
        messages.append({"role": "user", "content": user_text})
        resp = httpx.post(
            BACKEND,
            json={"messages": messages, "useRag": True, "improvedRag": True,
                  "sessionId": session_id},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        reply = data.get("reply", "")
        sources = data.get("sources", []) or []
        task_state = data.get("taskState") or {}
        rag_meta = data.get("ragMeta") or {}
        abstained = bool(rag_meta.get("abstained"))
        recap = bool(rag_meta.get("recap"))

        messages.append({"role": "assistant", "content": reply})
        goal = (task_state.get("goal") or "").strip()
        if goal:
            goals_seen.append(goal)

        turns_log.append({
            "user": user_text,
            "goal": goal,
            "n_sources": len(sources),
            "abstained": abstained,
            "recap": recap,
            "reply_head": reply[:90],
        })

    return {"name": scenario["name"], "session_id": session_id,
            "turns": turns_log, "goals_seen": goals_seen}


def check(result: dict) -> list[str]:
    """Вернуть список провалов инвариантов (пусто = всё зелёно)."""
    failures: list[str] = []
    turns = result["turns"]

    # (1) goal не теряется: как только он появился, дальше на каждом ходу непустой.
    first_goal_idx = next((i for i, t in enumerate(turns) if t["goal"]), None)
    if first_goal_idx is None:
        failures.append("goal так и не был установлен ни на одном ходу")
    else:
        for t in turns[first_goal_idx:]:
            if not t["goal"]:
                failures.append(
                    f"goal потерян на реплике: {t['user'][:60]!r}"
                )

    # (2) содержательность: обычный (не-recap) не-abstain ответ обязан иметь источники;
    #     recap-ответ отвечает из «памяти задачи» без кода-источника — его инвариант в том,
    #     что он НЕ уходит в abstain.
    for t in turns:
        if t.get("recap"):
            if t["abstained"]:
                failures.append(f"recap-ответ ушёл в abstain: {t['user'][:60]!r}")
        elif not t["abstained"] and t["n_sources"] == 0:
            failures.append(
                f"RAG-ответ без источников (не abstain): {t['user'][:60]!r}"
            )
    return failures


def main() -> int:
    results = []
    all_failures: list[str] = []
    for scenario in SCENARIOS:
        print(f"▶ {scenario['name']}")
        res = run_scenario(scenario)
        fails = check(res)
        res["failures"] = fails
        results.append(res)
        for t in res["turns"]:
            flag = "RECAP" if t.get("recap") else ("ABSTAIN" if t["abstained"] else f"{t['n_sources']} src")
            print(f"   • [{flag:>8}] goal={t['goal'][:50]!r}")
        if fails:
            all_failures.extend(f"[{scenario['name']}] {f}" for f in fails)
            print(f"   ✗ FAIL: {len(fails)} нарушений")
        else:
            print("   ✓ OK")

    write_report(results, all_failures)
    if all_failures:
        print(f"\n✗ ИТОГ: {len(all_failures)} нарушений — см. {REPORT.name}")
        return 1
    print(f"\n✓ ИТОГ: оба инварианта держатся во всех сценариях — см. {REPORT.name}")
    return 0


def write_report(results: list[dict], all_failures: list[str]) -> None:
    lines = [
        "# QA-отчёт — Задание 5 («память задачи» + источники)",
        "",
        "Прогон 2 многоходовых сценариев напрямую через backend "
        "(`127.0.0.1:8000`, минуя nginx). Проверяемые инварианты:",
        "",
        "1. `task_state.goal` не теряется по ходу диалога (единожды установлен — держится).",
        "2. Обычный RAG-ответ несёт источники; recap-вопрос отвечается из «памяти задачи» "
        "(без кода-источника) и не уходит в abstain. Сценарии идут в improved-режиме "
        "(rewrite + rerank).",
        "",
        f"**Итог:** {'✅ оба инварианта держатся' if not all_failures else f'❌ {len(all_failures)} нарушений'}.",
        "",
    ]
    for res in results:
        lines.append(f"## {res['name']}")
        lines.append(f"`session_id = {res['session_id']}`  ")
        status = "✅ OK" if not res["failures"] else f"❌ {len(res['failures'])} нарушений"
        lines.append(f"Статус: **{status}**")
        lines.append("")
        lines.append("| # | Реплика | goal (усечён) | Источников | abstain |")
        lines.append("|---|---|---|---|---|")
        for i, t in enumerate(res["turns"], 1):
            goal = (t["goal"][:45] + "…") if len(t["goal"]) > 45 else t["goal"]
            status = "recap" if t.get("recap") else ("да" if t["abstained"] else "нет")
            lines.append(
                f"| {i} | {t['user'][:55]} | {goal or '—'} | "
                f"{t['n_sources']} | {status} |"
            )
        lines.append("")
        if res["failures"]:
            lines.append("Нарушения:")
            lines.extend(f"- {f}" for f in res["failures"])
            lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())

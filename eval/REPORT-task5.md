# QA-отчёт — Задание 5 («память задачи» + источники)

Прогон 2 многоходовых сценариев напрямую через backend (`127.0.0.1:8000`, минуя nginx). Проверяемые инварианты:

1. `task_state.goal` не теряется по ходу диалога (единожды установлен — держится).
2. Обычный RAG-ответ несёт источники; recap-вопрос отвечается из «памяти задачи» (без кода-источника) и не уходит в abstain. Сценарии идут в improved-режиме (rewrite + rerank).

**Итог:** ✅ оба инварианта держатся.

## Jetchat: управление состоянием беседы
`session_id = qa-task5-53f4c53a-6c92-4008-addd-ceb8e844dfbc`  
Статус: **✅ OK**

| # | Реплика | goal (усечён) | Источников | abstain |
|---|---|---|---|---|
| 1 | In Jetchat, which class holds the conversation UI state | In Jetchat, which class holds the conversatio… | 1 | нет |
| 2 | What constructor parameters does that ConversationUiSta | In Jetchat, which class holds the conversatio… | 1 | нет |
| 3 | At which position does its addMessage() insert a new me | In Jetchat, which class holds the conversatio… | 0 | да |
| 4 | What fields does the Message data class have? | In Jetchat, which class holds the conversatio… | 0 | да |
| 5 | How is the message list backed so Compose observes chan | In Jetchat, which class holds the conversatio… | 0 | да |
| 6 | Which UI tests cover the conversation screen in the and | In Jetchat, which class holds the conversatio… | 2 | нет |
| 7 | Summarize what I've learned about Jetchat's conversatio | In Jetchat, which class holds the conversatio… | 0 | recap |

## JetNews: UI-state и обработка ошибок
`session_id = qa-task5-c6febb9d-6eb8-4cae-bd9f-a08473be48ce`  
Статус: **✅ OK**

| # | Реплика | goal (усечён) | Источников | abstain |
|---|---|---|---|---|
| 1 | In JetNews, I want to understand the home screen UI sta | In JetNews, understand the home screen UI sta… | 1 | нет |
| 2 | Which three common properties does that sealed interfac | In JetNews, understand the home screen UI sta… | 1 | нет |
| 3 | What fields does the ErrorMessage data class contain? | In JetNews, understand the home screen UI sta… | 1 | нет |
| 4 | How does HomeViewModel expose the UI state to the compo | In JetNews, understand the home screen UI sta… | 0 | да |
| 5 | How are error messages surfaced to the user in JetNews? | In JetNews, understand the home screen UI sta… | 0 | да |
| 6 | What are the two subtypes of the HomeUiState sealed int | In JetNews, understand the home screen UI sta… | 0 | да |
| 7 | Recap the JetNews home-state design we've discussed. | In JetNews, understand the home screen UI sta… | 0 | recap |

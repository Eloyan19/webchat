# QA-отчёт — Задание 5 («память задачи» + источники)

Прогон 2 многоходовых сценариев напрямую через backend (`127.0.0.1:8000`, минуя nginx). Проверяемые инварианты:

1. `task_state.goal` не теряется по ходу диалога (единожды установлен — держится).
2. У каждого не-abstain RAG-ответа есть источники (grounding не регрессировал).

**Итог:** ✅ оба инварианта держатся.

## Jetchat: управление состоянием беседы
`session_id = qa-task5-a74ebb39-e964-4aad-b974-931ca58eac12`  
Статус: **✅ OK**

| # | Реплика | goal (усечён) | Источников | abstain |
|---|---|---|---|---|
| 1 | In Jetchat, which class holds the conversation UI state | Identify the class holding conversation UI st… | 1 | нет |
| 2 | What constructor parameters does that ConversationUiSta | Identify the class holding conversation UI st… | 1 | нет |
| 3 | At which position does its addMessage() insert a new me | Identify the class holding conversation UI st… | 0 | да |
| 4 | What fields does the Message data class have? | Identify the class holding conversation UI st… | 1 | нет |
| 5 | How is the message list backed so Compose observes chan | Identify the class holding conversation UI st… | 0 | да |
| 6 | Which UI tests cover the conversation screen in the and | Identify the class holding conversation UI st… | 1 | нет |
| 7 | Summarize what I've learned about Jetchat's conversatio | Identify the class holding conversation UI st… | 1 | нет |

## JetNews: UI-state и обработка ошибок
`session_id = qa-task5-60bdc932-d4ff-4835-8a64-c16481439e6b`  
Статус: **✅ OK**

| # | Реплика | goal (усечён) | Источников | abstain |
|---|---|---|---|---|
| 1 | In JetNews, I want to understand the home screen UI sta | Understand the type of HomeUiState in JetNews… | 1 | нет |
| 2 | Which three common properties does that sealed interfac | Understand the type of HomeUiState in JetNews… | 0 | да |
| 3 | What fields does the ErrorMessage data class contain? | Understand the type of HomeUiState in JetNews… | 1 | нет |
| 4 | How does HomeViewModel expose the UI state to the compo | Understand the type of HomeUiState in JetNews… | 2 | нет |
| 5 | How are error messages surfaced to the user in JetNews? | Understand the type of HomeUiState in JetNews… | 0 | да |
| 6 | Which library does JetNews use for its networking layer | Understand the type of HomeUiState in JetNews… | 0 | да |
| 7 | Recap the JetNews home-state design we've discussed. | Understand the type of HomeUiState in JetNews… | 0 | да |

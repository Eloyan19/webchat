# QA-отчёт — Задание 5 («память задачи» + источники)

Прогон 2 многоходовых сценариев напрямую через backend (`127.0.0.1:8000`, минуя nginx). Проверяемые инварианты:

1. `task_state.goal` не теряется по ходу диалога (единожды установлен — держится).
2. У каждого не-abstain RAG-ответа есть источники (grounding не регрессировал).

**Итог:** ✅ оба инварианта держатся.

## Jetchat: управление состоянием беседы
`session_id = qa-task5-2d4fb6a8-805a-43a3-a165-53ff0697df6f`  
Статус: **✅ OK**

| # | Реплика | goal (усечён) | Источников | abstain |
|---|---|---|---|---|
| 1 | In Jetchat, which class holds the conversation UI state | In Jetchat, which class holds the conversatio… | 1 | нет |
| 2 | What constructor parameters does that ConversationUiSta | In Jetchat, which class holds the conversatio… | 1 | нет |
| 3 | At which position does its addMessage() insert a new me | In Jetchat, which class holds the conversatio… | 0 | да |
| 4 | What fields does the Message data class have? | In Jetchat, which class holds the conversatio… | 1 | нет |
| 5 | How is the message list backed so Compose observes chan | In Jetchat, which class holds the conversatio… | 0 | да |
| 6 | Which UI tests cover the conversation screen in the and | In Jetchat, which class holds the conversatio… | 0 | да |
| 7 | Summarize what I've learned about Jetchat's conversatio | In Jetchat, which class holds the conversatio… | 1 | нет |

## JetNews: UI-state и обработка ошибок
`session_id = qa-task5-7a8931e5-d491-4239-83f8-8a0daeecf93d`  
Статус: **✅ OK**

| # | Реплика | goal (усечён) | Источников | abstain |
|---|---|---|---|---|
| 1 | In JetNews, I want to understand the home screen UI sta | понять тип HomeUiState в JetNews и его подтип… | 1 | нет |
| 2 | Which three common properties does that sealed interfac | понять тип HomeUiState в JetNews и его подтип… | 0 | да |
| 3 | What fields does the ErrorMessage data class contain? | понять тип HomeUiState в JetNews и его подтип… | 1 | нет |
| 4 | How does HomeViewModel expose the UI state to the compo | понять тип HomeUiState в JetNews и его подтип… | 3 | нет |
| 5 | How are error messages surfaced to the user in JetNews? | понять тип HomeUiState в JetNews и его подтип… | 0 | да |
| 6 | Which library does JetNews use for its networking layer | понять тип HomeUiState в JetNews и его подтип… | 0 | да |
| 7 | Recap the JetNews home-state design we've discussed. | понять тип HomeUiState в JetNews и его подтип… | 0 | да |

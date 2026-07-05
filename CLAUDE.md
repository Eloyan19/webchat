# CLAUDE.md — Web Chat (DeepSeek + RAG)

## Среда
- Claude Code работает на VPS **jorchik.com**. Деплой: systemd + nginx (паттерн как у
  MCP-сервера в Android-проекте `../AI_Challenge_2_3_4_5/`).
- **RAM VPS 3.8 ГБ** → локальные Ollama-модели ≤3B (`qwen2.5:3b`). DeepSeek — облако,
  лимит не касается.
- Соседние репозитории: `../rag/` — RAG-пайплайн (свой репо/CLAUDE.md), зовём его
  **по HTTP** (`RAG_URL`), не импортом через границу проектов; `../AI_Challenge_2_3_4_5/`
  — Android-приложение, **⏸ разработка приостановлена — не смотреть и не трогать**.

## Проект
Простой веб-чат поверх DeepSeek: история (localStorage), переключаемый RAG. Без
оркестрации, выбора стратегий, тюнинга параметров — намеренно минимально.
**Стек:** TypeScript · React · Vite · Python · FastAPI · httpx · localStorage.

## Архитектура (инварианты)
- Браузер → свой backend → DeepSeek. **Браузер НЕ ходит в DeepSeek напрямую**
  (CORS + ключ не должен утечь в клиент).
- Ключ `DEEPSEEK_API_KEY` — только env/`.env`, НЕ в git.
- Реальный API: `POST https://api.deepseek.com/v1/chat/completions`, OpenAI-совместимый,
  модели `deepseek-chat` / `deepseek-reasoner`.
- История — localStorage, модель `{role, content, ts}[]`.
- Контекст — `takeLast(20)` (+ скользящее summary позже).
- RAG-toggle обрабатывается на backend; RAG-сервис наружу не торчит.

## Grounding-инварианты (цитаты / источники / «не знаю»)
- **С RAG ответ обязан быть обоснован.** Генерация с контекстом идёт в JSON-режиме
  DeepSeek (`response_format={"type":"json_object"}`): модель возвращает
  `{"answer", "used":[{"id","quote"}]}`. Чанки в промпте нумеруются `[1..n]`.
- **Валидация цитат — анти-галлюцинации.** `parse_grounded_reply` оставляет только те
  цитаты, что дословно (по нормализованным пробелам) встречаются в тексте своего чанка;
  выдуманные отбрасываются (`ragMeta.quotesDropped`). Источник = `file :: section` + `quote`.
- **Гейт «не знаю» (никакого отката на знания модели).** `fetch_rag_context` ставит порог
  на `rerank_score` (`RERANK_THRESHOLD`), иначе на cosine `score` (`RAG_SIMILARITY_THRESHOLD`).
  Если ни один чанк не прошёл — `ragMeta.abstained=true`, backend отдаёт заранее заданный
  `ABSTAIN_REPLY` («не знаю, уточните») **без вызова генерации**. Порог в обоих режимах.
- Без RAG (`useRag=false`) поведение не меняется — обычный текст, без JSON и источников.
- Контракт `../rag /search` НЕ меняли: `chunk_id` не вводили, источник — `file :: section`.
- Eval-контракт — `eval/compare.py`: cited-прогон + авто-проверки (источники/цитаты) +
  LLM-судья grounded + набор off-topic для проверки abstain. Отчёт — `eval/REPORT.md`.

## Роль Claude — советник
Пользователь изучает LLM/агентов/веб-разработку — не все паттерны ему известны.
Подмечай упущенные возможности Claude Code (агенты, хуки, worktree, /loop, фоновые
задачи), лучшие паттерны, ограничения текущего решения. Одно короткое замечание в
конце ответа — достаточно, не превращай ответ в лекцию.

## Агенты (persona-агенты через Agent(model:, prompt:))

| Агент | Модель | Когда |
|---|---|---|
| 🏗️ ARCHITECT | opus | структура, границы фронт/backend/RAG, выбор паттерна |
| ⚛️ FRONTEND DEVELOPER | sonnet | React, TypeScript, hooks, state, Vite |
| ⚙️ BACKEND DEVELOPER | sonnet | Python/FastAPI, httpx, async, DeepSeek-прокси, RAG; ревьюит и Python-код |
| 🔍 CODE REVIEWER | sonnet | ревью TS/React (Python-ревью берёт BACKEND DEVELOPER) |
| 🎨 UI/UX SPECIALIST | sonnet | адаптивный CSS, accessibility (a11y), UX |
| 🛡️ SECURITY AUDITOR | opus | OWASP Web/API Top 10: XSS, CORS, утечка ключа, инъекции, secrets |
| 🧠 LLM ENGINEER | opus | промпт RAG-подстановки, управление контекстом, DeepSeek API |
| 🧪 QA ENGINEER | sonnet | Vitest (unit), Playwright (e2e) |
| 🐛 DEBUG SPECIALIST | opus | root-cause анализ багов |
| ⚡ PERFORMANCE ENGINEER | opus | размер бандла, рендер, сетевой waterfall (опционально) |

**Ревьюер по технологии:** TS/React → CODE REVIEWER; Python → BACKEND DEVELOPER.
**fresh agent** (`subagent_type: "claude"`) с самодостаточным промптом предпочтительнее
fork для persona-ролей.

## Оркестрация (принципы)
1. Параллельно — независимые задачи. 2. Последовательно — когда результат нужен
следующему. 3. Минимальный контекст каждому агенту. 4. Worktree-изоляция для
параллельного кода. 5. Оркестратор синтезирует. 6. Модель по роли. 7. Фоновые
агенты (`run_in_background`), если результат не нужен немедленно.
- `/code-review` medium — после блока изменений 2+ файлов с логикой.
- Explore — до работы, если фиксишь паттерн / меняешь сигнатуру / ищешь call sites.

## Plan Mode — гейт перед входом
Перед `EnterPlanMode` проверь: нужен ли доменный эксперт (ARCHITECT / SECURITY AUDITOR /
LLM ENGINEER / PERFORMANCE ENGINEER / DEBUG SPECIALIST)?
- ДА → сначала запусти эксперта в обычном режиме (промпт ≤200 слов: ключевые решения и
  риски), дождись вывода, ПОТОМ `EnterPlanMode`.
- НЕТ (чистый FRONTEND/BACKEND, архитектура не меняется) → можно сразу.
Внутри Plan Mode следуй его шаблону, фазы не переупорядочивай.

# Бриф: веб-чат с DeepSeek + RAG (итеративное выполнение в loop)

> Это план для **холодного** Claude Code, запущенного из `/root/repos/webchat/`.
> Выполняй задачи **строго по порядку, по одной**: сделал → прогнал Verify →
> закоммитил → следующая. Не забегай вперёд. Задачи с 👤 CHECKPOINT требуют человека
> (UI/UX автономно не проверить) — остановись и попроси проверить глазами.

## Как исполнять (loop)

1. Первая задача со статусом «TODO».
2. Сделай ровно её (файлы указаны). 3. Прогони **Verify** — не прошло, чини.
4. Закоммить (сообщение = заголовок задачи). 5. 👤 CHECKPOINT — стоп, зови человека.
6. Следующая.

## Расположение и стек (решено)

```
Проект:   /root/repos/webchat/   (ОТДЕЛЬНЫЙ git-репозиторий, свой CLAUDE.md)
Соседи:   /root/repos/rag/                  (RAG-пайплайн, свой репо и CLAUDE.md)
          /root/repos/AI_Challenge_2_3_4_5/ (Android-приложение)

Браузер:  TypeScript + React (Vite)     → webchat/frontend/
Backend:  Python FastAPI на VPS         → webchat/backend/
              └─ POST /chat  → проксирует DeepSeek (+ RAG toggle)
RAG:      живёт в ../rag/ (отдельный репо) — зовём по HTTP (RAG_URL), НЕ импортом
Персист:  localStorage в браузере (без серверной БД)
```

## Зафиксированные решения (не пересматривать)

- **Браузер НЕ ходит в DeepSeek напрямую** (CORS + утечка ключа) — только через backend.
- **Ключ** `DEEPSEEK_API_KEY` — env/`.env`, НЕ в git. **Уже положен** в `backend/.env`.
- **DeepSeek API**: `POST https://api.deepseek.com/v1/chat/completions`, OpenAI-совместимый,
  модели `deepseek-chat` / `deepseek-reasoner`. Достижим с VPS (проверено).
- **История** — localStorage, модель `{role, content, ts}[]`.
- **Контекст**: v1 = `takeLast(20)`. Скользящее summary — поздняя задача 12.
- **Кнопка очистки** = полный сброс (сообщения + summary + localStorage), с confirm.
- **RAG-toggle** на backend; RAG-сервис зовётся по localhost HTTP, наружу не торчит.
- **RAM VPS 3.8 ГБ** → локальные Ollama ≤3B. К DeepSeek (облако) не относится.

## Prerequisites (человек/агент, ДО зависимых задач)

- [x] `DEEPSEEK_API_KEY` в `backend/.env` — сделано.
- [x] **Node.js + npm установлены** — v22.23.1 / npm 10.9.8 (NodeSource 22.x). Готово.
- [ ] Python venv — `python3 -m venv backend/.venv` (или переиспользовать rag/.venv).
- [ ] **RAG-сервис `/search`** — предусловие задачи 9. Строится и деплоится **отдельной
      сессией из `../rag/`** (свой репо/CLAUDE.md; бриф `../rag/serve-retrieval.md`) на
      `127.0.0.1:8100`. webchat только ходит к нему по HTTP — RAG-логику не трогает.
      Задачи 1–8 от него не зависят (можно делать параллельно). До подъёма — RAG-toggle
      мокать. Контракт `/search` — в задаче 9 ниже.

---

## Задачи

### 1. CLAUDE.md + git init · TODO
Создать `webchat/CLAUDE.md` c содержимым из блока «CLAUDE.md (готовый)» ниже.
Проверить, что `.gitignore` уже есть (создан: `backend/.env`, `.env`, `node_modules/`,
`dist/`, `__pycache__/`, `.venv/`). Затем `git init` + первый коммит (CLAUDE.md, BRIEF.md,
.gitignore). **Verify:** `git -C /root/repos/webchat check-ignore backend/.env` печатает
путь (ключ игнорируется); `git log` содержит первый коммит; CLAUDE.md на месте.

### 2. Скаффолд проекта · TODO
`frontend/` (Vite React-TS: `npm create vite@latest frontend -- --template react-ts`) и
`backend/` (FastAPI: `main.py` c `/health`→`{"ok":true}`, `requirements.txt`: fastapi,
uvicorn, httpx, python-dotenv). Требует Node (см. prerequisites). **Verify:**
`cd frontend && npm install && npm run build` проходит; `uvicorn main:app` стартует,
`curl :PORT/health` → `{"ok":true}`.

### 3. Backend `/chat` — прокси DeepSeek (без истории/RAG) · TODO
`POST /chat` принимает `{messages:[{role,content}]}`, читает `DEEPSEEK_API_KEY` (dotenv),
шлёт в DeepSeek (`deepseek-chat`) через httpx, возвращает `{reply}`. Ошибки → 502 с телом.
CORS middleware. **Verify:** `curl -X POST :PORT/chat -d '{"messages":[{"role":"user","content":"say hi in one word"}]}'` → реальный ответ.

### 4. Фронт: минимальный чат · TODO · 👤 CHECKPOINT
Поле ввода + Send + список сообщений; на Send дёргает `/chat`. **Verify:** `npm run build`
проходит; человек вводит сообщение → видит ответ.

### 5. Многоходовость · TODO
Слать весь массив `messages` каждый запрос. **Verify:** follow-up со ссылкой на прошлый
ответ → модель помнит.

### 6. Персистентность localStorage · TODO
Сохранять `messages` в localStorage, восстанавливать при загрузке. **Verify:** перезагрузка
страницы → история на месте.

### 7. Кнопка очистки · TODO · 👤 CHECKPOINT
Кнопка → confirm → чистит messages + localStorage (+ summary позже). **Verify:** человек:
клик → пусто; перезагрузка → остаётся пусто.

### 8. Guard контекста `takeLast(20)` · TODO
Обрезать историю до последних 20 перед отправкой. **Verify:** лог числа исходящих ≤20.

### 9. RAG на backend · TODO · (LLM ENGINEER для промпта)
**Предусловие:** RAG-сервис `/search` поднят на `127.0.0.1:8100` (см. prerequisites /
`../rag/serve-retrieval.md`). webchat — только HTTP-клиент, RAG-логику не реализует.
Генерацию по-прежнему делает **DeepSeek**; у rag берём лишь чанки (retrieval).

Контракт (согласован с `../rag/`):
```
POST http://127.0.0.1:8100/search
req:  {"query": "<последний вопрос>", "k": 5, "strategy": "structural"}
resp: {"chunks": [{"file","section","text","score"}, ...]}
```
`/chat` принимает `useRag:bool`. При `true`: последний вопрос → POST `${RAG_URL}/search`
→ из `chunks` собрать system-сообщение с нумерованными источниками
`[1] file :: section\n<text>` + инструкция «отвечай по контексту, иначе скажи» → дальше
обычный DeepSeek-вызов. `RAG_URL` из env (default `http://127.0.0.1:8100`). Сервис
недоступен → отвечать без RAG (graceful degradation), не падать. **Verify:** `curl` с
`useRag:true` про корпус → ответ со ссылками на файлы; `false` — без.

### 10. Фронт: тумблер RAG · TODO · 👤 CHECKPOINT
Переключатель RAG on/off → `useRag` в запросе; показывать источники. **Verify:** человек:
тумблер меняет поведение.

### 11. Деплой на VPS · TODO
systemd-сервис (uvicorn) + nginx `location` для backend + раздача `npm run build` статики.
Ключ в systemd unit (не в git). **Verify:** публичный URL работает end-to-end.

### 12. (Позже) Скользящее summary · TODO
Выпавшее за окно `takeLast(20)` суммаризовать одним вызовом `deepseek-chat`, хранить в
state+localStorage, prepend system-msg. **Verify:** длинный диалог помнит ранний факт.

---

## CLAUDE.md (готовый — сохранить в задаче 1 как `webchat/CLAUDE.md`)

```markdown
# CLAUDE.md — Web Chat (DeepSeek + RAG)

## Среда
- Claude Code работает на VPS **jorchik.com**. Деплой: systemd + nginx (паттерн как у
  MCP-сервера в Android-проекте `../AI_Challenge_2_3_4_5/`).
- **RAM VPS 3.8 ГБ** → локальные Ollama-модели ≤3B (`qwen2.5:3b`). DeepSeek — облако,
  лимит не касается.
- Соседние репозитории: `../rag/` — RAG-пайплайн (свой репо/CLAUDE.md), зовём его
  **по HTTP** (`RAG_URL`), не импортом через границу проектов; `../AI_Challenge_2_3_4_5/`
  — Android-приложение.

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
```
```

## Возможности Claude Code (советник)
- **Запуск loop:** «выполняй BRIEF.md по задачам, по одной, verify+commit каждую,
  стоп на 👤 CHECKPOINT».
- `/code-review` medium после задач 3, 9, 11.
- Долгие шаги (`npm install`, deploy, установка Node) — `run_in_background: true`.
- UI автономно не верифицируется — 👤 CHECKPOINT (4, 7, 10) требуют человека.

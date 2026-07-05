# webchat — веб-чат поверх DeepSeek с RAG

Простой веб-чат: история в localStorage, переключаемый RAG-режим, ответы с
**источниками, цитатами и режимом «не знаю»**. Часть воркспейса `~/repos`
(см. корневой `../CLAUDE.md`); RAG-извлечение делает сосед `../rag/` по HTTP.

**Стек:** TypeScript · React · Vite · Python · FastAPI · httpx · localStorage.
**Прод:** systemd + nginx на jorchik.com (см. `deploy/README.md`).

## Архитектура

```
Браузер ──▶ nginx (jorchik.com) ──▶ backend :8000 ──▶ DeepSeek API (облако)
                                          └──▶ rag /search :8100 (retrieval)
```

- Браузер ходит только в свой backend; ключ `DEEPSEEK_API_KEY` наружу не утекает
  (только `backend/.env`, в git не попадает).
- RAG-toggle обрабатывается на backend; сервис `../rag/` наружу не выставлен.
- Инварианты и правила работы — в `CLAUDE.md`.

## Режимы RAG

| Режим | Что делает |
|---|---|
| Без RAG | обычный ответ DeepSeek из знаний модели |
| RAG (plain) | одностадийное извлечение top-k + порог-гейт |
| Улучшенный RAG | query rewrite (multi-turn) + rerank + порог-фильтр |

## Цитаты, источники и режим «не знаю» (анти-галлюцинации)

Сделано в рамках задачи `citations-task.md` (2026-07-05):

- **Обязательные источники и цитаты.** С включённым RAG генерация идёт в JSON-режиме
  DeepSeek: модель возвращает ответ + для каждого использованного чанка **дословную
  цитату**. Backend валидирует, что цитата реально является подстрокой текста чанка
  (`parse_grounded_reply`); выдуманные цитаты отбрасываются. Источник = `file :: section`,
  в ответе — ссылки `[i]`. В UI под ответом видны источники и цитаты.
- **Режим «не знаю».** Если релевантность найденных чанков ниже порога (или после
  валидации не осталось ни одной цитаты) — ассистент отвечает «Не знаю: в источниках
  нет ответа, уточните вопрос» и **не** отвечает из собственных знаний модели. Порог
  работает в обоих RAG-режимах.
- **Проверка.** `eval/compare.py` гоняет контрольные вопросы в cited-режиме, проверяет
  наличие источников/цитат, дословность и обоснованность (LLM-судья DeepSeek), а на
  наборе off-topic — срабатывание режима «не знаю». Отчёт — `eval/REPORT.md`.
  Последний прогон: источники 11/12 · цитаты 11/12 · grounded 11/11 · off-topic abstain 5/5.

## Запуск (dev)

```sh
# backend (:8000) — нужен ../rag на :8100 и ключ в backend/.env
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
echo "DEEPSEEK_API_KEY=<ключ>" > .env
.venv/bin/uvicorn main:app --port 8000

# frontend
cd frontend && npm install && npm run dev
```

## Структура

- `backend/main.py` — FastAPI-прокси: `/chat` (DeepSeek + RAG, grounding), `/health`.
- `frontend/src/` — React-приложение (`App.tsx`, `api.ts`, `types.ts`).
- `eval/` — сравнение режимов и grounding-проверки (`compare.py`, `REPORT.md`).
- `deploy/` — systemd-юнит и nginx-конфиг (`deploy/README.md`).
- `CLAUDE.md` — инварианты и правила для Claude Code. `BRIEF.md` — исходный план.

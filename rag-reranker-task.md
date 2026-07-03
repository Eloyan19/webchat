# Задача для сессии в `../rag/`: cross-encoder reranker в `/search`

> Скопируй этот файл как задание Claude, работающему **в контексте репозитория
> `/root/repos/rag/`** (у него свой CLAUDE.md / `serve-retrieval.md`). Он реализует
> вторую стадию ретривала — реранкинг. Клиент (`webchat`) уже готов и вызывает новый
> контракт с graceful-деградацией, так что менять webchat не нужно.

## Контекст
`rag` — retrieval-сервис (FAISS + эмбеддинги), поднят systemd-юнитом `rag-search.service`
на `127.0.0.1:8100`, эндпоинт `POST /search`. Сосед `webchat` (FastAPI-прокси к DeepSeek)
ходит к нему по HTTP и делает генерацию сам. Сейчас `/search` — одностадийный:
эмбеддинг запроса → top-k по FAISS → возврат чанков. Косинусные скоры «сжаты»
(в теме ~0.66–0.73, off-topic ~0.50–0.59), поэтому одного порога мало — нужен
**cross-encoder reranker** как вторая стадия.

## Что нужно сделать
Добавить в `/search` опциональный второй этап: после FAISS-поиска top-`k` кандидатов
переоценить пары `(query, chunk.text)` cross-encoder-моделью и **вернуть чанки,
переупорядоченные по убыванию rerank-скора**, добавив поле `rerank_score`.

### Текущий контракт (не ломать обратную совместимость)
```
POST /search
req:  {"query": str, "k": int, "strategy": "structural"}
resp: {"chunks": [{"file","section","text","score"}, ...]}   # score = cosine
```

### Новый контракт
```
req:  {"query": str, "k": int, "strategy": "structural", "rerank": bool}   # rerank default false
resp: {"chunks": [{"file","section","text","score","rerank_score"}, ...]}
```
Требования:
- `rerank` **по умолчанию `false`** → поведение ровно как сейчас (реранк не считается,
  `rerank_score` можно не добавлять). Сейчас webchat в plain-режиме шлёт `rerank:false`,
  а в improved — `rerank:true`; лишнее поле уже игнорируется, но добавь его в модель
  `SearchRequest` явно (`rerank: bool = False`).
- При `rerank:true`: взять все `k` FAISS-кандидатов, посчитать cross-encoder-скор для
  каждой пары `(query, text)`, **отсортировать по `rerank_score` убыв.** и вернуть в этом
  порядке. `score` (cosine) **сохранить** в каждом чанке — webchat фильтрует по нему.
- Не менять число возвращаемых чанков (верни все `k` переупорядоченными); обрезание/порог
  делает клиент. (Опционально можешь принять `rerank_top_n`, но это не требуется.)

## Модель (рекомендация под VPS 3.8 ГБ RAM, где ещё крутится ollama)
- `cross-encoder/ms-marco-MiniLM-L-6-v2` через `sentence-transformers` (`CrossEncoder`),
  CPU, веса ~80 МБ. Грузить **лениво, singleton** (первый запрос с `rerank:true`), чтобы
  не раздувать RSS при старте и не мешать plain-запросам.
- ⚠️ **RAM-риск:** `sentence-transformers`+`torch` (CPU) в резиденте это ~0.5–1 ГБ.
  Вместе с ollama-моделями может быть тесно. Обязательно:
  - поставь **CPU-only torch** (без CUDA), проверь `free -m` до/после первого реранка;
  - если тесно — вариант полегче: `cross-encoder/ms-marco-MiniLM-L-2-v2` или ONNX-инференс
    (`fastembed`/`optimum`), без torch. Выбор оставляю на тебя после замера RAM.
- Конфиг через env/`config.py`: `RERANK_MODEL`, `RERANK_ENABLED` (kill-switch), `RERANK_DEVICE=cpu`.
  Если модель не загрузилась — логировать и **вернуть FAISS-порядок** (не падать; для клиента
  это выглядит как обычный ответ, деградация мягкая).

## Куда встроить
В `serve.py`: расширить `SearchRequest` (`rerank: bool = False`), в обработчике `/search`
после получения FAISS-кандидатов (перед формированием ответа) — если `rerank`, прогнать
реранк-функцию (вынеси в отдельный модуль, напр. `rerank.py`) и переупорядочить.

## Проверка (acceptance)
1. Обратная совместимость: `{"query":"navigation","k":5,"strategy":"structural"}` (без
   `rerank`) → как раньше, тот же формат, тот же порядок.
2. Реранк: `{"query":"What does addMessage do in Jetchat ConversationUiState?","k":20,
   "strategy":"structural","rerank":true}` → у чанков есть `rerank_score`, порядок по нему
   убывающий, и **`ConversationUiState.kt` поднимается в топ** (сейчас на cosine он тонет).
3. RAM: замерь `free -m` до/после первого реранка, зафиксируй в PR/README.
4. e2e через webchat: `curl -X POST http://127.0.0.1:8000/chat -d '{"useRag":true,
   "improvedRag":true,"messages":[{"role":"user","content":"What does addMessage do in
   Jetchat ConversationUiState?"}]}'` → в `sources` появляется `ConversationUiState.kt`.
5. Прогнать `webchat/eval/compare.py` — hit-rate `improved` должен догнать/обогнать `plain`
   (сейчас 7/10 vs 9/10 именно из-за отсутствия реранка).

## Как это использует webchat (уже реализовано, менять не нужно)
- improved-режим: `RAG_K_BEFORE=20` кандидатов с `rerank:true` → фильтр по cosine
  `score >= RAG_SIMILARITY_THRESHOLD` (0.62) → топ `RAG_K_AFTER=5` в присланном (reranked)
  порядке → system-контекст для DeepSeek.
- Поэтому от тебя нужно: (а) сохранить `score` (cosine) в ответе, (б) вернуть чанки уже
  отсортированными по `rerank_score`. Всё остальное клиент делает сам.
- (На будущее: когда реранк заработает, webchat, возможно, переключит порог на
  `rerank_score` — но для этого этапа cosine-порога достаточно, отдельной координации не
  требуется.)

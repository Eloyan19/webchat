import json
import os
import re

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from memory import TaskMemory, TaskState

load_dotenv()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
RAG_URL = os.getenv("RAG_URL", "http://127.0.0.1:8100")

# Plain RAG: single-stage retrieval. Improved RAG: retrieve more (k_before),
# rerank + threshold-filter, keep k_after.
RAG_K = int(os.getenv("RAG_K", "5"))
RAG_K_BEFORE = int(os.getenv("RAG_K_BEFORE", "20"))
RAG_K_AFTER = int(os.getenv("RAG_K_AFTER", "5"))
# Relevance floor for the "don't know" gate. Preferred signal is the cross-encoder
# rerank_score returned by the RAG service (wide separation: in-domain ~ >=0,
# off-topic ~ -11); fallback to the compressed cosine score when the service does
# not rerank (in-domain ~0.66-0.73, off-topic ~0.5-0.59). A question whose best
# chunk sits below the floor gets an honest "не знаю" instead of a guessed answer.
RERANK_THRESHOLD = float(os.getenv("RERANK_THRESHOLD", "-6.0"))
RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.62"))

# Canned reply when retrieval finds nothing relevant enough. We deliberately do
# NOT fall back to the model's own knowledge here — with RAG on, an unsupported
# answer is a hallucination risk, so we abstain and ask the user to refine.
ABSTAIN_REPLY = (
    "Не знаю: в найденных источниках нет ответа на этот вопрос. "
    "Уточните или переформулируйте вопрос."
)

# Per-session «память задачи» (in-memory, эфемерная). См. memory.py.
MEMORY = TaskMemory()
# Сколько последних сообщений подавать в LLM-апдейт task_state: дельта диалога.
# Сам накопленный state уже несёт историю, всю переписку дублировать не нужно.
TASK_STATE_RECENT = 6
# Кап на длину массивов state — держим промпт генерации компактным и гасим дрейф.
TASK_STATE_CAP = 8

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    useRag: bool = False
    improvedRag: bool = False
    # Идентификатор сессии от фронта — ключ «памяти задачи». Без него state
    # не хранится (каждый ход стартует с пустого): память чисто опциональна.
    sessionId: str | None = None


class Source(BaseModel):
    file: str
    section: str
    score: float
    rerank_score: float | None = None
    # Стабильный id чанка из rag /search — сквозная адресация источника в UI.
    chunk_id: int | None = None
    # Verbatim fragment of this chunk that the model used, validated as a real
    # substring of the chunk text (anti-hallucination). None only on fallback paths.
    quote: str | None = None


@app.get("/health")
def health():
    return {"ok": True}


async def call_deepseek(
    messages: list[dict], api_key: str, response_format: dict | None = None
) -> str:
    """Single DeepSeek chat completion. Raises httpx errors / KeyError on failure.

    Pass response_format={"type": "json_object"} to force a JSON reply (used for
    grounded, cited answers). The prompt must mention JSON for this mode to work.
    """
    payload: dict = {"model": DEEPSEEK_MODEL, "messages": messages}
    if response_format is not None:
        payload["response_format"] = response_format
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            DEEPSEEK_API_URL,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
        )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


async def rewrite_query(messages: list[dict], last_user: str, api_key: str) -> str:
    """Rewrite the last question into a standalone retrieval query using dialog
    context (resolve pronouns/references). Falls back to last_user on any error."""
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in messages[-6:])
    rewrite_msgs = [
        {
            "role": "system",
            "content": (
                "Ты переписываешь последний вопрос пользователя в ОДИН самостоятельный "
                "ВОПРОС для поиска по базе исходного кода (Google compose-samples). "
                "Раскрой местоимения и отсылки к прошлым репликам (напр. «этот класс» → "
                "конкретное имя из диалога), но СОХРАНИ форму естественного вопроса — НЕ "
                "превращай в набор ключевых слов (это ухудшает семантический поиск). "
                "Верни ТОЛЬКО вопрос, без кавычек и пояснений."
            ),
        },
        {
            "role": "user",
            "content": f"Диалог:\n{convo}\n\nПерепиши последний вопрос в поисковый запрос.",
        },
    ]
    try:
        rewritten = (await call_deepseek(rewrite_msgs, api_key)).strip()
        return rewritten or last_user
    except (httpx.HTTPError, KeyError, ValueError):
        return last_user


async def rag_search(query: str, k: int, rerank: bool) -> list[dict]:
    """Call the RAG /search service. Returns chunks, or [] on any failure."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{RAG_URL}/search",
                json={"query": query, "k": k, "strategy": "structural", "rerank": rerank},
            )
        resp.raise_for_status()
        data = resp.json()
        return data.get("chunks", []) if isinstance(data, dict) else []
    except (httpx.HTTPError, ValueError):
        return []


def _task_state_block(task_state: TaskState | None) -> str:
    """Компактный блок «Память задачи» для system-prompt генерации.

    Помечен как НАМЕРЕНИЕ (не источник фактов/цитат): помогает модели понять цель
    диалога, но цитаты по-прежнему берутся только из пронумерованного контекста.
    Пустой state -> пустая строка (ничего не подмешиваем)."""
    if task_state is None:
        return ""
    parts: list[str] = []
    if task_state.goal:
        parts.append(f"- Цель: {task_state.goal}")
    if task_state.constraints:
        parts.append(f"- Ограничения: {'; '.join(task_state.constraints)}")
    if task_state.terms:
        parts.append(f"- Термины: {'; '.join(task_state.terms)}")
    if task_state.clarified:
        parts.append(f"- Уточнено: {'; '.join(task_state.clarified)}")
    if not parts:
        return ""
    body = "\n".join(parts)
    return (
        "Память задачи (для понимания намерения пользователя, это НЕ источник фактов "
        "и НЕ источник цитат — отвечай и цитируй только из контекста ниже):\n"
        f"{body}\n\n"
    )


def build_system_prompt(chunks: list[dict], task_state: TaskState | None = None) -> str:
    """System prompt that pins the model to the context and forces a cited JSON
    reply. Chunks are numbered [1..n]; the model must echo those ids in `used`.
    An optional task_state block is prepended as intent context (not a quote source)."""
    blocks = [
        f"[{i}] {c.get('file', '')} :: {c.get('section', '')}\n{c.get('text', '')}"
        for i, c in enumerate(chunks, start=1)
    ]
    context = "\n\n".join(blocks)
    return (
        f"{_task_state_block(task_state)}"
        "Ты отвечаешь на вопрос пользователя, опираясь ТОЛЬКО на приведённый ниже "
        "контекст из базы знаний. Верни СТРОГО один JSON-объект такого вида:\n"
        '{"answer": "...", "used": [{"id": <номер источника>, "quote": "<дословный фрагмент>"}]}\n'
        "Правила:\n"
        "- answer: ответ на языке вопроса; ссылайся на источники по номеру в квадратных "
        "скобках, например [1].\n"
        "- used: для КАЖДОГО источника, на который опираешься, укажи id (номер [i]) и quote — "
        "фрагмент, СКОПИРОВАННЫЙ ПОБУКВЕННО из текста источника НА ЯЗЫКЕ ОРИГИНАЛА (обычно "
        "английский или код). НЕ переводи цитату на русский, не сокращай, не меняй пробелы, "
        "регистр и пунктуацию — quote должна дословно встречаться в тексте источника, иначе "
        "она будет отброшена. answer пиши на языке вопроса, но quote — только из оригинала.\n"
        "- Если в контексте НЕТ ответа на вопрос — верни в answer честное «Не знаю: в источниках "
        "нет ответа на этот вопрос, уточните вопрос» и пустой used: [].\n"
        "- Не выдумывай факты и цитаты вне контекста.\n\n"
        f"Контекст:\n{context}"
    )


def _normalize(text: str) -> str:
    """Collapse whitespace and lowercase, so quote validation tolerates trivial
    reflow differences between the model's copy and the raw chunk text."""
    return re.sub(r"\s+", " ", text).strip().lower()


def parse_grounded_reply(
    raw: str, chunks: list[dict]
) -> tuple[str, list[Source], int]:
    """Parse the model's JSON reply into (answer, validated_sources, quotes_dropped).

    Each `used` entry is kept only if its id maps to a presented chunk AND its quote
    is a real substring of that chunk's text — a fabricated quote is dropped. On any
    JSON failure we degrade gracefully: raw text as the answer, no sources.
    """
    by_id = {i: c for i, c in enumerate(chunks, start=1)}
    try:
        data = json.loads(raw)
        answer = str(data.get("answer", "")).strip()
        used = data.get("used", []) or []
    except (json.JSONDecodeError, TypeError, AttributeError):
        return raw.strip(), [], 0

    if not answer:
        answer = raw.strip()

    sources: list[Source] = []
    dropped = 0
    seen: set[int] = set()
    for item in used if isinstance(used, list) else []:
        if not isinstance(item, dict):
            dropped += 1
            continue
        try:
            cid = int(item.get("id"))
        except (TypeError, ValueError):
            dropped += 1
            continue
        quote = str(item.get("quote", "")).strip()
        chunk = by_id.get(cid)
        if chunk is None or not quote:
            dropped += 1
            continue
        if _normalize(quote) not in _normalize(chunk.get("text", "")):
            dropped += 1  # quote not found verbatim in the chunk -> hallucinated
            continue
        if cid in seen:
            continue
        seen.add(cid)
        sources.append(Source(
            file=chunk.get("file", ""), section=chunk.get("section", ""),
            score=chunk.get("score", 0.0), rerank_score=chunk.get("rerank_score"),
            chunk_id=chunk.get("chunk_id"), quote=quote,
        ))
    return answer, sources, dropped


# Prepended (as an extra system turn) on a retry when the first cited attempt yielded
# no validated quote — reminds the model to copy the quote verbatim, in the source's
# original language, instead of paraphrasing or translating it.
QUOTE_RETRY_NUDGE = (
    "ВАЖНО: в прошлый раз ни одна цитата не совпала с текстом источника дословно. "
    "Скопируй каждую quote ПОБУКВЕННО из текста источника на ЯЗЫКЕ ОРИГИНАЛА "
    "(не переводи, не сокращай, не меняй пробелы и регистр). Если дословной цитаты "
    "действительно нет — верни used: []."
)


async def generate_grounded(
    messages: list[dict], chunks: list[dict], api_key: str
) -> tuple[str, list[Source], int, bool]:
    """Cited JSON generation with ONE retry on empty quotes.

    The verbatim-quote gate occasionally false-abstains: retrieval found the answer
    but the model paraphrased/translated its quote, so none validated. Before giving
    up we retry once with a firmer instruction (a cheap way to cut false «не знаю»
    without weakening the guarantee — a real quote is still required). Returns
    (reply, sources, quotes_dropped, retried). messages[0] is the context system
    prompt; the nudge goes right after it."""
    raw = await call_deepseek(messages, api_key, response_format={"type": "json_object"})
    reply, sources, dropped = parse_grounded_reply(raw, chunks)
    if sources:
        return reply, sources, dropped, False
    retry_messages = [
        messages[0], {"role": "system", "content": QUOTE_RETRY_NUDGE}, *messages[1:]
    ]
    raw = await call_deepseek(retry_messages, api_key, response_format={"type": "json_object"})
    reply, sources, dropped = parse_grounded_reply(raw, chunks)
    return reply, sources, dropped, True


TASK_STATE_SYSTEM = (
    "Ты ведёшь «память задачи» диалога — структурированное состояние. Верни СТРОГО "
    "один JSON-объект такого вида:\n"
    '{"goal": "<строка>", "constraints": ["..."], "terms": ["..."], "clarified": ["..."]}\n'
    "Смысл полей: goal — главная цель/вопрос пользователя в диалоге; constraints — "
    "зафиксированные ограничения и требования; terms — важные термины/сущности; "
    "clarified — что пользователь уже уточнил или решил.\n"
    "Правила обновления (ОБНОВЛЯЙ ИНКРЕМЕНТАЛЬНО поверх текущего состояния):\n"
    "- Сохраняй текущий goal, если пользователь его ЯВНО не сменил; не переформулируй "
    "уже записанное.\n"
    "- Массивы: объединяй с текущими, добавляй только НОВОЕ, убирай дубли по смыслу.\n"
    "- Ничего не выдумывай — бери только то, что реально есть в сообщениях.\n"
    f"- В каждом массиве держи не более {TASK_STATE_CAP} самых релевантных пунктов, "
    "вытесняя устаревшие; формулировки — короткие.\n"
    "- Если данных нет — верни пустые: goal \"\", массивы []. Верни ТОЛЬКО JSON."
)


def _dedup_cap(items: list) -> list[str]:
    """Нормализовать список строк: привести к str, выкинуть пустые, снять дубли
    (без учёта регистра), обрезать до TASK_STATE_CAP. Защита от разрастания и от
    мусора, который может вернуть модель."""
    seen: set[str] = set()
    out: list[str] = []
    for it in items if isinstance(items, list) else []:
        s = str(it).strip()
        key = s.lower()
        if not s or key in seen:
            continue
        seen.add(key)
        out.append(s)
        if len(out) >= TASK_STATE_CAP:
            break
    return out


async def update_task_state(
    state: TaskState, recent_msgs: list[dict], api_key: str
) -> TaskState:
    """Отдельный DeepSeek-вызов: обновить task_state из (текущий state + свежие
    сообщения). При любой ошибке (сеть/JSON) возвращаем ПРЕЖНИЙ state — обновление
    памяти не должно рушить ответ пользователю."""
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in recent_msgs)
    messages = [
        {"role": "system", "content": TASK_STATE_SYSTEM},
        {
            "role": "user",
            "content": (
                f"Текущее состояние задачи (JSON):\n{state.model_dump_json()}\n\n"
                f"Свежие сообщения диалога:\n{convo}\n\n"
                "Верни обновлённое состояние задачи одним JSON-объектом."
            ),
        },
    ]
    try:
        raw = await call_deepseek(
            messages, api_key, response_format={"type": "json_object"}
        )
        data = json.loads(raw)
        if not isinstance(data, dict):
            return state
        goal = str(data.get("goal", "") or "").strip() or state.goal
        return TaskState(
            goal=goal,
            constraints=_dedup_cap(data.get("constraints", [])),
            terms=_dedup_cap(data.get("terms", [])),
            clarified=_dedup_cap(data.get("clarified", [])),
        )
    except (httpx.HTTPError, KeyError, ValueError, TypeError, AttributeError):
        return state


async def fetch_rag_context(query: str, improved: bool) -> tuple[list[dict], dict]:
    """Retrieve and relevance-gate chunks for `query`.

    Plain mode: single-stage top-RAG_K, cosine floor. Improved mode: retrieve
    RAG_K_BEFORE (asking the service to rerank), floor on rerank_score, keep top
    RAG_K_AFTER. Returns (kept_chunks, meta). Empty kept_chunks -> the caller
    abstains ("не знаю"). We never silently answer from the model's own knowledge.
    """
    k = RAG_K_BEFORE if improved else RAG_K
    chunks = await rag_search(query, k, rerank=improved)
    meta: dict = {"k_requested": k, "k_returned": len(chunks), "improved": improved}
    if not chunks:
        meta["abstained"] = True
        return [], meta

    # Floor on rerank_score when the service provides it (cleaner separation),
    # else on the cosine score.
    has_rerank = chunks[0].get("rerank_score") is not None
    signal, threshold = (
        ("rerank_score", RERANK_THRESHOLD) if has_rerank
        else ("score", RAG_SIMILARITY_THRESHOLD)
    )
    kept = [c for c in chunks if c.get(signal, 0.0) >= threshold]
    if improved:
        kept = kept[:RAG_K_AFTER]
    meta.update({
        "filter_signal": signal, "threshold": threshold,
        "k_after_filter": len(kept), "filtered_out": len(chunks) - len(kept),
        "abstained": len(kept) == 0,
    })
    return kept, meta


@app.post("/chat")
async def chat(req: ChatRequest):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return JSONResponse(status_code=502, content={"error": "DEEPSEEK_API_KEY not set"})

    messages = [m.model_dump() for m in req.messages]
    sources: list[Source] = []
    rewritten_query: str | None = None
    rag_meta: dict = {}
    grounded_chunks: list[dict] | None = None

    # «Память задачи»: читаем текущее состояние сессии (пустое, если sessionId нет
    # или сессия новая). Инъектируем в промпт генерации; обновляем в конце хода.
    if req.sessionId:
        async with MEMORY.lock:
            task_state = MEMORY.get(req.sessionId)
    else:
        task_state = TaskState()

    if req.useRag:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), None
        )
        if last_user:
            search_query = last_user
            # Query rewrite only helps when there is prior dialog to resolve
            # (pronouns/references); on a standalone question it adds noise.
            if req.improvedRag and len(messages) > 1:
                search_query = await rewrite_query(messages, last_user, api_key)
                rewritten_query = search_query
            grounded_chunks, rag_meta = await fetch_rag_context(
                search_query, req.improvedRag
            )
            # Relevance gate: nothing passed the floor -> abstain, do not generate.
            # Ничего не зафиксировали -> task_state не обновляем, возвращаем как есть.
            if rag_meta.get("abstained"):
                return {
                    "reply": ABSTAIN_REPLY,
                    "sources": [],
                    "rewrittenQuery": rewritten_query,
                    "ragMeta": rag_meta,
                    "taskState": task_state.model_dump(),
                }
            messages = [
                {"role": "system", "content": build_system_prompt(grounded_chunks, task_state)},
                *messages,
            ]

    try:
        if grounded_chunks:
            reply, sources, dropped, retried = await generate_grounded(
                messages, grounded_chunks, api_key
            )
            rag_meta["quotesDropped"] = dropped
            rag_meta["retried"] = retried
            # No validated quote survived even after the retry (model paraphrased/
            # hallucinated, cited nothing, or returned empty/non-JSON). We must not
            # surface an answer with dangling [i] refs and no sources — abstain to
            # keep the "every answer is grounded in a real quote" guarantee.
            if not sources:
                rag_meta["abstained"] = True
                rag_meta["modelAbstained"] = True
                return {
                    "reply": ABSTAIN_REPLY,
                    "sources": [],
                    "rewrittenQuery": rewritten_query,
                    "ragMeta": rag_meta,
                    "taskState": task_state.model_dump(),
                }
        else:
            reply = await call_deepseek(messages, api_key)
    except httpx.HTTPError as e:
        return JSONResponse(status_code=502, content={"error": f"DeepSeek request failed: {e}"})
    except (KeyError, ValueError) as e:
        return JSONResponse(status_code=502, content={"error": f"Bad DeepSeek response: {e}"})

    # Обновляем «память задачи» ПОСЛЕ успешного ответа, отдельным LLM-вызовом. Только
    # для grounded-ответа с реальными источниками и при наличии sessionId. LLM-вызов
    # вне Lock (не блокируем другие сессии на время сети); Lock — лишь на быстрый R/W.
    if req.sessionId and grounded_chunks and sources:
        recent = [
            {"role": m.role, "content": m.content} for m in req.messages
        ][-TASK_STATE_RECENT:]
        recent.append({"role": "assistant", "content": reply})
        updated = await update_task_state(task_state, recent, api_key)
        async with MEMORY.lock:
            MEMORY.set(req.sessionId, updated)
        task_state = updated

    return {
        "reply": reply,
        "sources": [s.model_dump() for s in sources],
        "rewrittenQuery": rewritten_query,
        "ragMeta": rag_meta,
        "taskState": task_state.model_dump(),
    }

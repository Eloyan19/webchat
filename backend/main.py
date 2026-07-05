import json
import os
import re

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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


class Source(BaseModel):
    file: str
    section: str
    score: float
    rerank_score: float | None = None
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
                "Ты переписываешь вопрос пользователя в ОДИН самостоятельный поисковый "
                "запрос для базы знаний по исходному коду (Google compose-samples). "
                "Раскрывай местоимения и отсылки к прошлым репликам, добавляй ключевые "
                "термины. Верни ТОЛЬКО запрос — без кавычек, без пояснений."
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


def build_system_prompt(chunks: list[dict]) -> str:
    """System prompt that pins the model to the context and forces a cited JSON
    reply. Chunks are numbered [1..n]; the model must echo those ids in `used`."""
    blocks = [
        f"[{i}] {c.get('file', '')} :: {c.get('section', '')}\n{c.get('text', '')}"
        for i, c in enumerate(chunks, start=1)
    ]
    context = "\n\n".join(blocks)
    return (
        "Ты отвечаешь на вопрос пользователя, опираясь ТОЛЬКО на приведённый ниже "
        "контекст из базы знаний. Верни СТРОГО один JSON-объект такого вида:\n"
        '{"answer": "...", "used": [{"id": <номер источника>, "quote": "<дословный фрагмент>"}]}\n'
        "Правила:\n"
        "- answer: ответ на языке вопроса; ссылайся на источники по номеру в квадратных "
        "скобках, например [1].\n"
        "- used: для КАЖДОГО источника, на который опираешься, укажи id (номер [i]) и quote — "
        "фрагмент, СКОПИРОВАННЫЙ ДОСЛОВНО из текста этого источника (без изменений, перевода "
        "и сокращений).\n"
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
            quote=quote,
        ))
    return answer, sources, dropped


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
            if rag_meta.get("abstained"):
                return {
                    "reply": ABSTAIN_REPLY,
                    "sources": [],
                    "rewrittenQuery": rewritten_query,
                    "ragMeta": rag_meta,
                }
            messages = [
                {"role": "system", "content": build_system_prompt(grounded_chunks)},
                *messages,
            ]

    try:
        if grounded_chunks:
            raw = await call_deepseek(
                messages, api_key, response_format={"type": "json_object"}
            )
            reply, sources, dropped = parse_grounded_reply(raw, grounded_chunks)
            rag_meta["quotesDropped"] = dropped
            # No validated quote survived (model paraphrased/hallucinated, cited
            # nothing, or returned empty/non-JSON). We must not surface an answer
            # with dangling [i] refs and no sources — abstain to keep the "every
            # answer is grounded in a real quote" guarantee.
            if not sources:
                rag_meta["abstained"] = True
                rag_meta["modelAbstained"] = True
                return {
                    "reply": ABSTAIN_REPLY,
                    "sources": [],
                    "rewrittenQuery": rewritten_query,
                    "ragMeta": rag_meta,
                }
        else:
            reply = await call_deepseek(messages, api_key)
    except httpx.HTTPError as e:
        return JSONResponse(status_code=502, content={"error": f"DeepSeek request failed: {e}"})
    except (KeyError, ValueError) as e:
        return JSONResponse(status_code=502, content={"error": f"Bad DeepSeek response: {e}"})

    return {
        "reply": reply,
        "sources": [s.model_dump() for s in sources],
        "rewrittenQuery": rewritten_query,
        "ragMeta": rag_meta,
    }

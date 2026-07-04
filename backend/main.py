import os

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

# Plain RAG: single-stage retrieval, no filter.
RAG_K = int(os.getenv("RAG_K", "5"))
# Improved RAG: retrieve more (k_before), filter by cosine threshold, keep k_after.
RAG_K_BEFORE = int(os.getenv("RAG_K_BEFORE", "20"))
RAG_K_AFTER = int(os.getenv("RAG_K_AFTER", "5"))
# Relevance cutoffs for the improved-mode filter. Preferred signal is the
# cross-encoder rerank_score returned by the RAG service (wide separation:
# in-domain ~ >=0, off-topic ~ -11), with a fallback to the compressed cosine
# score if the service doesn't rerank (in-domain ~0.66-0.73, off-topic ~0.5-0.59).
RERANK_THRESHOLD = float(os.getenv("RERANK_THRESHOLD", "-6.0"))
RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.62"))

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


@app.get("/health")
def health():
    return {"ok": True}


async def call_deepseek(messages: list[dict], api_key: str) -> str:
    """Single DeepSeek chat completion. Raises httpx errors / KeyError on failure."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            DEEPSEEK_API_URL,
            json={"model": DEEPSEEK_MODEL, "messages": messages},
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


def build_context(chunks: list[dict]) -> tuple[str, list[Source]]:
    blocks = []
    sources: list[Source] = []
    for i, c in enumerate(chunks, start=1):
        file = c.get("file", "")
        section = c.get("section", "")
        text = c.get("text", "")
        blocks.append(f"[{i}] {file} :: {section}\n{text}")
        sources.append(Source(
            file=file, section=section,
            score=c.get("score", 0.0), rerank_score=c.get("rerank_score"),
        ))
    context = "\n\n".join(blocks)
    system_prompt = (
        "Ты отвечаешь на вопрос пользователя, опираясь ТОЛЬКО на приведённый ниже "
        "контекст из базы знаний. Если в контексте нет ответа — честно скажи, что "
        "информации в источниках нет, и не выдумывай. Где уместно, ссылайся на "
        "источники по номеру в квадратных скобках, например [1].\n\n"
        f"Контекст:\n{context}"
    )
    return system_prompt, sources


async def fetch_rag_context(
    query: str, improved: bool
) -> tuple[str | None, list[Source], dict]:
    """Retrieve context for `query`.

    Plain mode: single-stage top-RAG_K, no filter.
    Improved mode: retrieve RAG_K_BEFORE (asking the service to rerank), drop
    chunks below RAG_SIMILARITY_THRESHOLD, keep top RAG_K_AFTER.

    Returns (system_prompt|None, sources, meta). None system_prompt -> answer
    without RAG context (graceful degradation).
    """
    k = RAG_K_BEFORE if improved else RAG_K
    chunks = await rag_search(query, k, rerank=improved)
    meta = {"k_requested": k, "k_returned": len(chunks), "improved": improved}

    if improved:
        # Filter on the cross-encoder rerank_score when the service provides it
        # (far cleaner separation); fall back to the cosine score otherwise.
        has_rerank = bool(chunks) and chunks[0].get("rerank_score") is not None
        if has_rerank:
            signal, threshold = "rerank_score", RERANK_THRESHOLD
        else:
            signal, threshold = "score", RAG_SIMILARITY_THRESHOLD
        kept = [c for c in chunks if c.get(signal, 0.0) >= threshold][:RAG_K_AFTER]
        meta.update(
            {"filter_signal": signal, "threshold": threshold,
             "k_after_filter": len(kept), "filtered_out": len(chunks) - len(kept)}
        )
        chunks = kept

    if not chunks:
        return None, [], meta

    system_prompt, sources = build_context(chunks)
    return system_prompt, sources, meta


@app.post("/chat")
async def chat(req: ChatRequest):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return JSONResponse(status_code=502, content={"error": "DEEPSEEK_API_KEY not set"})

    messages = [m.model_dump() for m in req.messages]
    sources: list[Source] = []
    rewritten_query: str | None = None
    rag_meta: dict = {}

    if req.useRag:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), None
        )
        if last_user:
            search_query = last_user
            # Query rewrite only helps when there is prior dialog to resolve
            # (pronouns/references). On a standalone question it can only add
            # noise words and drift retrieval, so skip it.
            if req.improvedRag and len(messages) > 1:
                search_query = await rewrite_query(messages, last_user, api_key)
                rewritten_query = search_query
            system_prompt, sources, rag_meta = await fetch_rag_context(
                search_query, req.improvedRag
            )
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}, *messages]

    try:
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

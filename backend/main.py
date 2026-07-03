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
RAG_K = 5

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


class Source(BaseModel):
    file: str
    section: str
    score: float


@app.get("/health")
def health():
    return {"ok": True}


async def fetch_rag_context(query: str) -> tuple[str | None, list[Source]]:
    """Query the RAG service. Returns (system_prompt, sources).

    On any failure returns (None, []) so /chat degrades gracefully to a
    plain DeepSeek call instead of erroring out.
    """
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{RAG_URL}/search",
                json={"query": query, "k": RAG_K, "strategy": "structural"},
            )
        resp.raise_for_status()
        data = resp.json()
        chunks = data.get("chunks", []) if isinstance(data, dict) else []
    except (httpx.HTTPError, ValueError):
        return None, []

    if not chunks:
        return None, []

    blocks = []
    sources: list[Source] = []
    for i, c in enumerate(chunks, start=1):
        file = c.get("file", "")
        section = c.get("section", "")
        text = c.get("text", "")
        blocks.append(f"[{i}] {file} :: {section}\n{text}")
        sources.append(Source(file=file, section=section, score=c.get("score", 0.0)))

    context = "\n\n".join(blocks)
    system_prompt = (
        "Ты отвечаешь на вопрос пользователя, опираясь ТОЛЬКО на приведённый ниже "
        "контекст из базы знаний. Если в контексте нет ответа — честно скажи, что "
        "информации в источниках нет, и не выдумывай. Где уместно, ссылайся на "
        "источники по номеру в квадратных скобках, например [1].\n\n"
        f"Контекст:\n{context}"
    )
    return system_prompt, sources


@app.post("/chat")
async def chat(req: ChatRequest):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return JSONResponse(status_code=502, content={"error": "DEEPSEEK_API_KEY not set"})

    messages = [m.model_dump() for m in req.messages]
    sources: list[Source] = []

    if req.useRag:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), None
        )
        if last_user:
            system_prompt, sources = await fetch_rag_context(last_user)
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}, *messages]

    payload = {"model": DEEPSEEK_MODEL, "messages": messages}
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(DEEPSEEK_API_URL, json=payload, headers=headers)
    except httpx.HTTPError as e:
        return JSONResponse(status_code=502, content={"error": f"DeepSeek request failed: {e}"})

    if resp.status_code != 200:
        return JSONResponse(status_code=502, content={"error": resp.text})

    data = resp.json()
    reply = data["choices"][0]["message"]["content"]
    return {"reply": reply, "sources": [s.model_dump() for s in sources]}

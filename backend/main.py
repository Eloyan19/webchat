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


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/chat")
async def chat(req: ChatRequest):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return JSONResponse(status_code=502, content={"error": "DEEPSEEK_API_KEY not set"})

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [m.model_dump() for m in req.messages],
    }
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
    return {"reply": reply}

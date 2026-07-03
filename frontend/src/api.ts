import type { Message, Source } from './types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
const MAX_CONTEXT = 20

export interface ChatResult {
  reply: string
  sources: Source[]
}

export async function sendChat(messages: Message[], useRag: boolean): Promise<ChatResult> {
  const outgoing = messages.slice(-MAX_CONTEXT)
  console.log(`[chat] sending ${outgoing.length} messages (history ${messages.length}), useRag=${useRag}`)
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: outgoing.map((m) => ({ role: m.role, content: m.content })),
      useRag,
    }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Backend error ${res.status}: ${text}`)
  }
  const data = await res.json()
  return { reply: data.reply as string, sources: (data.sources ?? []) as Source[] }
}

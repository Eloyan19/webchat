import type { Message } from './types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
const MAX_CONTEXT = 20

export async function sendChat(messages: Message[]): Promise<string> {
  const outgoing = messages.slice(-MAX_CONTEXT)
  console.log(`[chat] sending ${outgoing.length} messages (history ${messages.length})`)
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: outgoing.map((m) => ({ role: m.role, content: m.content })),
    }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Backend error ${res.status}: ${text}`)
  }
  const data = await res.json()
  return data.reply as string
}

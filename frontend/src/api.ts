import type { Message, Source } from './types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
const CHAT_TOKEN = import.meta.env.VITE_CHAT_TOKEN ?? ''
export const MAX_CONTEXT = 20

export interface ChatResult {
  reply: string
  sources: Source[]
  rewrittenQuery: string | null
}

type WireMessage = { role: string; content: string }

function headers(): Record<string, string> {
  const h: Record<string, string> = { 'Content-Type': 'application/json' }
  if (CHAT_TOKEN) h.Authorization = `Bearer ${CHAT_TOKEN}`
  return h
}

async function postChat(
  messages: WireMessage[],
  useRag: boolean,
  improvedRag: boolean,
): Promise<ChatResult> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ messages, useRag, improvedRag }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Backend error ${res.status}: ${text}`)
  }
  const data = await res.json()
  return {
    reply: data.reply as string,
    sources: (data.sources ?? []) as Source[],
    rewrittenQuery: (data.rewrittenQuery ?? null) as string | null,
  }
}

export async function sendChat(
  messages: Message[],
  useRag: boolean,
  improvedRag: boolean = false,
  summary: string = '',
): Promise<ChatResult> {
  const window = messages.slice(-MAX_CONTEXT)
  const wire: WireMessage[] = window.map((m) => ({ role: m.role, content: m.content }))
  if (summary) {
    wire.unshift({
      role: 'system',
      content: `Краткое содержание более ранней части диалога:\n${summary}`,
    })
  }
  console.log(
    `[chat] sending ${wire.length} messages (history ${messages.length}, summary=${summary ? 'yes' : 'no'}, useRag=${useRag}, improvedRag=${improvedRag})`,
  )
  return postChat(wire, useRag, improvedRag)
}

// Condense the messages that fell out of the takeLast(MAX_CONTEXT) window into a
// running summary, folding in any previous summary. One deepseek-chat call.
export async function summarize(previousSummary: string, dropped: Message[]): Promise<string> {
  const convo = dropped.map((m) => `${m.role}: ${m.content}`).join('\n')
  const prompt =
    `Существующее summary диалога:\n${previousSummary || '(пусто)'}\n\n` +
    `Новые сообщения, которые нужно добавить в summary:\n${convo}\n\n` +
    `Обнови summary: в 3–6 предложениях сохрани ключевые факты, решения, имена и числа ` +
    `из всего диалога. Верни только текст summary, без пояснений.`
  const { reply } = await postChat([{ role: 'user', content: prompt }], false, false)
  return reply.trim()
}

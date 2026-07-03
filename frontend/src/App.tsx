import { useEffect, useState } from 'react'
import { sendChat } from './api'
import type { Message } from './types'
import './App.css'

const STORAGE_KEY = 'webchat.messages'

function loadMessages(): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? (parsed as Message[]) : []
  } catch {
    return []
  }
}

function App() {
  const [messages, setMessages] = useState<Message[]>(loadMessages)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [useRag, setUseRag] = useState(false)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
  }, [messages])

  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return

    const userMsg: Message = { role: 'user', content: text, ts: Date.now() }
    const next = [...messages, userMsg]
    setMessages(next)
    setInput('')
    setError(null)
    setLoading(true)

    try {
      const { reply, sources } = await sendChat(next, useRag)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: reply, ts: Date.now(), sources },
      ])
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  function handleClear() {
    if (messages.length === 0) return
    if (!window.confirm('Очистить всю историю чата? Это действие необратимо.')) return
    setMessages([])
    setError(null)
    localStorage.removeItem(STORAGE_KEY)
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat">
      <header className="chat-header">
        <h1>Web Chat</h1>
        <button
          type="button"
          className="clear"
          onClick={handleClear}
          disabled={messages.length === 0}
        >
          Очистить
        </button>
      </header>

      <div className="messages">
        {messages.length === 0 && (
          <p className="empty">Напиши сообщение, чтобы начать.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg msg-${m.role}`}>
            <span className="role">{m.role === 'user' ? 'Вы' : 'DeepSeek'}</span>
            <span className="content">{m.content}</span>
            {m.sources && m.sources.length > 0 && (
              <div className="sources">
                <span className="sources-title">Источники:</span>
                <ol>
                  {m.sources.map((s, j) => (
                    <li key={j}>
                      <code>{s.file}</code> :: {s.section}
                    </li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="msg msg-assistant">…</div>}
      </div>

      {error && <div className="error">{error}</div>}

      <label className="rag-toggle">
        <input
          type="checkbox"
          checked={useRag}
          onChange={(e) => setUseRag(e.target.checked)}
        />
        RAG (поиск по базе знаний)
      </label>

      <div className="composer">
        <input
          type="text"
          value={input}
          placeholder="Сообщение…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button type="button" onClick={handleSend} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  )
}

export default App

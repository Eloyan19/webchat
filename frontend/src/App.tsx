import { useEffect, useState } from 'react'
import { MAX_CONTEXT, resetSessionId, sendChat, summarize } from './api'
import type { Message, TaskState } from './types'
import './App.css'

const STORAGE_KEY = 'webchat.messages'
const SUMMARY_KEY = 'webchat.summary'
const SUMMARIZED_COUNT_KEY = 'webchat.summarizedCount'

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

// Есть ли что показывать в панели памяти (иначе не рендерим пустой блок).
function hasTaskState(s: TaskState): boolean {
  return Boolean(
    s.goal || s.constraints.length || s.terms.length || s.clarified.length,
  )
}

// Подсписок панели «Состояние задачи»; пустой массив не рендерится.
function TaskList({ label, items }: { label: string; items: string[] }) {
  if (!items || items.length === 0) return null
  return (
    <div className="task-group">
      <span className="task-label">{label}:</span>
      <ul>
        {items.map((it, i) => (
          <li key={i}>{it}</li>
        ))}
      </ul>
    </div>
  )
}

function App() {
  const [messages, setMessages] = useState<Message[]>(loadMessages)
  const [summary, setSummary] = useState<string>(
    () => localStorage.getItem(SUMMARY_KEY) ?? '',
  )
  const [summarizedCount, setSummarizedCount] = useState<number>(
    () => Number(localStorage.getItem(SUMMARIZED_COUNT_KEY)) || 0,
  )
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // Мини-чат: RAG всегда включён по умолчанию (источники всегда).
  const [useRag, setUseRag] = useState(true)
  // Улучшенный режим (rewrite + rerank + фильтр) по умолчанию ВКЛ: без rewrite
  // multi-turn теряет местоимения («тот класс»/«его») и уходит в ложное «не знаю».
  const [improvedRag, setImprovedRag] = useState(true)
  // «Память задачи» — последнее состояние, присланное backend по этой сессии.
  const [taskState, setTaskState] = useState<TaskState | null>(null)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
  }, [messages])

  useEffect(() => {
    localStorage.setItem(SUMMARY_KEY, summary)
  }, [summary])

  useEffect(() => {
    localStorage.setItem(SUMMARIZED_COUNT_KEY, String(summarizedCount))
  }, [summarizedCount])

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
      // Fold messages that fell out of the takeLast(MAX_CONTEXT) window into a
      // running summary so the model keeps early facts. Failure here is
      // non-fatal — we just send without an updated summary.
      let curSummary = summary
      const dropTo = Math.max(0, next.length - MAX_CONTEXT)
      if (dropTo > summarizedCount) {
        try {
          curSummary = await summarize(curSummary, next.slice(summarizedCount, dropTo))
          setSummary(curSummary)
          setSummarizedCount(dropTo)
        } catch {
          /* keep previous summary; older messages just drop out of context */
        }
      }

      const { reply, sources, rewrittenQuery, taskState: nextState } = await sendChat(
        next,
        useRag,
        useRag && improvedRag,
        curSummary,
      )
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: reply, ts: Date.now(), sources, rewrittenQuery },
      ])
      if (nextState) setTaskState(nextState)
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
    setSummary('')
    setSummarizedCount(0)
    setTaskState(null)
    setError(null)
    // Новая сессия -> backend стартует «память задачи» с чистого листа.
    resetSessionId()
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(SUMMARY_KEY)
    localStorage.removeItem(SUMMARIZED_COUNT_KEY)
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
            {m.rewrittenQuery && (
              <div className="rewritten">
                🔎 поисковый запрос: <em>{m.rewrittenQuery}</em>
              </div>
            )}
            {m.sources && m.sources.length > 0 && (
              <div className="sources">
                <span className="sources-title">Источники:</span>
                <ol>
                  {m.sources.map((s, j) => (
                    <li key={j}>
                      <code>{s.file}</code> :: {s.section}
                      {s.chunk_id != null && (
                        <span className="chunk-id"> #{s.chunk_id}</span>
                      )}
                      {s.quote && <blockquote className="quote">{s.quote}</blockquote>}
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

      {taskState && hasTaskState(taskState) && (
        <section className="task-state" aria-label="Состояние задачи">
          <h2 className="task-state-title">🧠 Состояние задачи</h2>
          {taskState.goal && (
            <p className="task-goal">
              <span className="task-label">Цель:</span> {taskState.goal}
            </p>
          )}
          <TaskList label="Ограничения" items={taskState.constraints} />
          <TaskList label="Термины" items={taskState.terms} />
          <TaskList label="Уточнено" items={taskState.clarified} />
        </section>
      )}

      <label className="rag-toggle">
        <input
          type="checkbox"
          checked={useRag}
          onChange={(e) => setUseRag(e.target.checked)}
        />
        RAG (поиск по базе знаний)
      </label>

      {useRag && (
        <label className="rag-toggle rag-toggle-nested">
          <input
            type="checkbox"
            checked={improvedRag}
            onChange={(e) => setImprovedRag(e.target.checked)}
          />
          Улучшенный RAG (query rewrite + фильтр/реранк)
        </label>
      )}

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

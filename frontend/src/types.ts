export type Role = 'user' | 'assistant'

export interface Source {
  file: string
  section: string
  score: number
  // Stable chunk id from the rag /search contract — through-addressing in the UI.
  chunk_id?: number
  // Verbatim fragment of the chunk the answer relied on (validated server-side).
  quote?: string
}

// «Память задачи» — структурированное состояние диалога, которое backend держит
// по session_id и обновляет каждый ход. Рендерится в панели «Состояние задачи».
export interface TaskState {
  goal: string
  constraints: string[]
  terms: string[]
  clarified: string[]
}

export interface Message {
  role: Role
  content: string
  ts: number
  sources?: Source[]
  rewrittenQuery?: string | null
}

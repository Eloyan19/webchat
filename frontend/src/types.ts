export type Role = 'user' | 'assistant'

export interface Source {
  file: string
  section: string
  score: number
  // Verbatim fragment of the chunk the answer relied on (validated server-side).
  quote?: string
}

export interface Message {
  role: Role
  content: string
  ts: number
  sources?: Source[]
  rewrittenQuery?: string | null
}

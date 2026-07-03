export type Role = 'user' | 'assistant'

export interface Source {
  file: string
  section: string
  score: number
}

export interface Message {
  role: Role
  content: string
  ts: number
  sources?: Source[]
}

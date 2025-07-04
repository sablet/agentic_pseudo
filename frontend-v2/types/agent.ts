export interface AgentInfo {
  agent_id: string
  parent_agent_id: string | null
  purpose: string
  context: string
  delegation_type: string
  status: "pending" | "in_progress" | "completed" | "failed" | "delegated"
  delegation_params?: Record<string, any>
  created_at: Date
  updated_at: Date
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant" | "system" | "system_notification"
  content: string
  timestamp: Date
  agent_id?: string // どのエージェントのチャットに属するか
  agent_proposal?: {
    purpose: string
    delegation_type: string
    context: string
    delegation_params?: Record<string, any>
  }
}

export interface AgentNode {
  id: string
  label: string
  status: AgentInfo["status"]
  x?: number
  y?: number
}

export interface AgentEdge {
  from: string
  to: string
  label?: string
}

export interface ChatSession {
  agent_id: string | null // nullはメインセッション
  agent_name: string
  messages: ChatMessage[]
}

// Data unit types for purposes and contexts
export type DataUnit = 
  | "market_analysis_report"
  | "competitor_comparison_table"
  | "customer_segment_data"
  | "pricing_strategy_document"
  | "feature_analysis_matrix"
  | "market_share_data"
  | "user_survey_results"
  | "financial_projections"
  | "risk_assessment_report"
  | "technical_specifications"
  | "compliance_checklist"
  | "performance_metrics"
  | "user_feedback_summary"
  | "integration_requirements"
  | "training_materials"
  | "business_requirements_document"
  | string // Allow custom values

export type ExecutionEngine = 
  | "gemini-2.5-flash"
  | "claude-code" 
  | "gpt-4o"
  | "gpt-4o-mini"
  | "claude-3.5-sonnet"
  | "gemini-1.5-pro"
  | string // Allow custom engines

export interface AgentInfo {
  agent_id: string
  parent_agent_id: string | null
  purpose: DataUnit
  context: DataUnit[]
  delegation_type: string
  status: "todo" | "doing" | "waiting" | "needs_input"
  execution_engine: ExecutionEngine
  delegation_params?: Record<string, any>
  created_at: Date
  updated_at: Date
  level: number // ユーザーが直接作成したエージェントはlevel0
}

export interface ConversationMessage {
  id: string
  role: "user" | "agent"
  content: string
  timestamp: Date
}

export interface ParentAgentSummary {
  agent_id: string
  purpose: string
  status: AgentInfo["status"]
  level: number
}

export interface ChildAgentSummary {
  agent_id: string
  purpose: string
  status: AgentInfo["status"]
  level: number
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

export interface ContextStatus {
  id: string
  name: string
  type: 'file' | 'text' | 'selection' | 'approval'
  required: boolean
  status: 'sufficient' | 'insufficient' | 'pending'
  description: string
  current_value?: any
}

export interface WaitingInfo {
  type: 'context' | 'approval' | 'dependency'
  description: string
  estimated_time?: string
  dependencies?: string[]
}

export interface AgentMetaInfo {
  agent_id: string
  purpose: string
  description: string
  level: number
  context_status: ContextStatus[]
  waiting_for: WaitingInfo[]
  execution_log: string[]
  progress_percentage: number
  conversation_history: ConversationMessage[]
  parent_agent_summary?: ParentAgentSummary | null
  child_agent_summaries: ChildAgentSummary[]
}

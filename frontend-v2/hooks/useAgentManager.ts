"use client"

import { useState, useCallback } from "react"
import type { AgentInfo, AgentMetaInfo, ContextStatus, DataUnit, ExecutionEngine } from "@/types/agent"


interface AgentTemplate {
  delegation_type: string
  purpose: DataUnit
  context: DataUnit[]
  execution_engine: ExecutionEngine
  parameters: Record<string, any>
}

export function useAgentManager() {
  // Create sample data with parent-child hierarchy
  const createSampleAgents = (): AgentInfo[] => {
    const now = new Date()
    
    // Level 0: Parent agent (user created)
    const parentAgent: AgentInfo = {
      agent_id: "agent_parent_12345",
      parent_agent_id: null,
      purpose: "market_analysis_report",
      context: ["business_requirements_document"],
      delegation_type: "包括的分析",
      status: "doing",
      execution_engine: "gemini-2.5-flash",
      delegation_params: {
        target_market: "SaaS業界",
        product_category: "プロジェクト管理ツール",
        timeline: "30日間"
      },
      created_at: new Date(now.getTime() - 3600000), // 1 hour ago
      updated_at: new Date(now.getTime() - 600000),  // 10 minutes ago
      level: 0,
    }

    // Level 1: Child agents (delegated by parent)
    const childAgent1: AgentInfo = {
      agent_id: "agent_competitor_67890",
      parent_agent_id: "agent_parent_12345",
      purpose: "competitor_comparison_table",
      context: ["market_analysis_report"], // Uses parent's purpose as context
      delegation_type: "競合分析",
      status: "doing",
      execution_engine: "claude-code",
      delegation_params: {
        target_competitors: ["Asana", "Trello", "Monday.com", "Notion", "Clickup"],
        analysis_depth: "detailed"
      },
      created_at: new Date(now.getTime() - 3000000), // 50 minutes ago
      updated_at: new Date(now.getTime() - 300000),  // 5 minutes ago
      level: 1,
    }

    const childAgent2: AgentInfo = {
      agent_id: "agent_customer_11111",
      parent_agent_id: "agent_parent_12345",
      purpose: "customer_segment_data",
      context: ["market_analysis_report"], // Uses parent's purpose as context
      delegation_type: "顧客分析",
      status: "needs_input",
      execution_engine: "gpt-4o",
      delegation_params: {
        survey_size: 500,
        target_segments: ["スタートアップ", "中小企業", "大企業"],
        industries: ["IT", "コンサルティング", "製造業", "金融"]
      },
      created_at: new Date(now.getTime() - 2800000), // 46 minutes ago
      updated_at: new Date(now.getTime() - 180000),  // 3 minutes ago
      level: 1,
    }

    const childAgent3: AgentInfo = {
      agent_id: "agent_pricing_22222",
      parent_agent_id: "agent_parent_12345",
      purpose: "pricing_strategy_document",
      context: ["competitor_comparison_table"], // Uses sibling's purpose as context (waiting for it)
      delegation_type: "価格戦略",
      status: "waiting",
      execution_engine: "claude-3.5-sonnet",
      delegation_params: {
        pricing_models: ["freemium", "tiered", "usage_based"],
        currency: "JPY"
      },
      created_at: new Date(now.getTime() - 2600000), // 43 minutes ago
      updated_at: new Date(now.getTime() - 120000),  // 2 minutes ago
      level: 1,
    }

    return [parentAgent, childAgent1, childAgent2, childAgent3]
  }

  const [agents, setAgents] = useState<AgentInfo[]>(createSampleAgents())

  const generateAgentId = useCallback(() => {
    return `agent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }, [])

  const createAgent = useCallback(
    (
      purpose: DataUnit,
      delegation_type: string,
      context: DataUnit[],
      execution_engine: ExecutionEngine = "gemini-2.5-flash",
      parent_agent_id: string | null = null,
      delegation_params?: Record<string, any>,
    ) => {
      // Calculate level based on parent
      let level = 0
      if (parent_agent_id) {
        const parentAgent = agents.find((a) => a.agent_id === parent_agent_id)
        level = parentAgent ? parentAgent.level + 1 : 1
      }

      const newAgent: AgentInfo = {
        agent_id: generateAgentId(),
        parent_agent_id,
        purpose,
        context,
        delegation_type,
        status: "todo",
        execution_engine,
        delegation_params,
        created_at: new Date(),
        updated_at: new Date(),
        level,
      }

      setAgents((prev) => [...prev, newAgent])
      return newAgent
    },
    [generateAgentId, agents],
  )

  const createAgentFromTemplate = useCallback(
    (template: AgentTemplate, customPurpose?: DataUnit, customContext?: DataUnit[]) => {
      const purpose = customPurpose || template.purpose
      const context = customContext || template.context

      return createAgent(purpose, template.delegation_type, context, template.execution_engine, null, template.parameters)
    },
    [createAgent],
  )

  const updateAgentStatus = useCallback((agent_id: string, status: AgentInfo["status"]) => {
    setAgents((prev) =>
      prev.map((agent) => (agent.agent_id === agent_id ? { ...agent, status, updated_at: new Date() } : agent)),
    )
  }, [])

  const executeAgent = useCallback(
    async (agent_id: string) => {
      updateAgentStatus(agent_id, "doing")
      console.log("Agent execution started:", agent_id)
      
      // TODO: Call backend API to start agent execution
      // const response = await fetch(`/api/agents/${agent_id}/execute`, { method: 'POST' })
    },
    [updateAgentStatus],
  )

  const completeAgent = useCallback(
    (agent_id: string) => {
      updateAgentStatus(agent_id, "todo") // Set back to todo for demo
      console.log("Agent completed:", agent_id)
    },
    [updateAgentStatus],
  )

  const fetchAgentMetaInfo = useCallback(
    async (agentId: string): Promise<AgentMetaInfo | null> => {
      try {
        // TODO: Replace with actual API call to backend
        // const response = await fetch(`/api/agents/${agentId}/meta`)
        // const data = await response.json()
        // return data

        // Mock implementation for demonstration
        const agent = agents.find((a) => a.agent_id === agentId)
        if (!agent) return null

        const mockContextStatus: ContextStatus[] = [
          {
            id: "ctx_file",
            name: "入力ファイル",
            type: "file",
            required: true,
            status: "insufficient",
            description: "処理対象となるファイルをアップロードしてください",
            current_value: null,
          },
          {
            id: "ctx_options",
            name: "処理オプション",
            type: "selection",
            required: true,
            status: "sufficient",
            description: "データ処理の方法を選択してください",
            current_value: "standard",
          },
        ]

        // Create specific data based on agent type
        const getAgentSpecificData = () => {
          switch (agent.agent_id) {
            case "agent_parent_12345":
              return {
                description: "新製品の市場投入戦略を策定するため、競合分析、顧客セグメント分析、価格戦略の3つの観点から包括的なマーケット分析を実施します。各分析は専門エージェントに委任し、統合的なレポートを作成します。",
                context_status: [
                  {
                    id: "ctx_market_scope",
                    name: "市場範囲定義",
                    type: "text" as const,
                    required: true,
                    status: "sufficient" as const,
                    description: "分析対象となる市場の範囲と製品カテゴリを定義",
                    current_value: "SaaS業界のプロジェクト管理ツール市場",
                  },
                  {
                    id: "ctx_timeline",
                    name: "分析期間",
                    type: "selection" as const,
                    required: true,
                    status: "sufficient" as const,
                    description: "マーケット分析の実施期間",
                    current_value: "30日間",
                  },
                ],
                waiting_for: [
                  {
                    type: "dependency" as const,
                    description: "子エージェント（競合分析、顧客分析、価格戦略）の完了待ち",
                    estimated_time: "15-20日",
                    dependencies: ["競合他社分析", "顧客セグメント分析", "価格戦略立案"],
                  },
                ],
                execution_log: [
                  "マーケット分析エージェント初期化完了",
                  "分析対象市場の定義完了: SaaS業界プロジェクト管理ツール",
                  "3つの専門分析エージェントを委任作成",
                  "→ 競合他社分析エージェント (実行中)",
                  "→ 顧客セグメント分析エージェント (コンテキスト待ち)",
                  "→ 価格戦略立案エージェント (依存関係待ち)",
                  "子エージェントの進捗監視中...",
                ],
                progress_percentage: 25,
              }
            
            case "agent_competitor_67890":
              return {
                description: "主要競合企業の詳細分析を実施し、機能比較、価格戦略、市場ポジショニングを調査します。収集したデータを基に競合比較表と市場マップを作成し、親エージェントに結果を報告します。",
                context_status: [
                  {
                    id: "ctx_competitors",
                    name: "分析対象競合企業",
                    type: "text" as const,
                    required: true,
                    status: "sufficient" as const,
                    description: "詳細分析を行う競合企業のリスト",
                    current_value: "Asana, Trello, Monday.com, Notion, Clickup",
                  },
                  {
                    id: "ctx_analysis_framework",
                    name: "分析フレームワーク",
                    type: "selection" as const,
                    required: true,
                    status: "sufficient" as const,
                    description: "競合分析で使用する分析手法",
                    current_value: "機能・価格・市場シェア分析",
                  },
                ],
                waiting_for: [],
                execution_log: [
                  "競合分析エージェント初期化完了",
                  "分析対象5社の基本情報収集完了",
                  "Asanaの機能・価格分析 完了",
                  "Trelloの機能・価格分析 完了",
                  "Monday.comの機能・価格分析 実行中...",
                  "Notionの機能・価格分析 待機中",
                  "Clickupの機能・価格分析 待機中",
                ],
                progress_percentage: 60,
              }
            
            case "agent_customer_11111":
              return {
                description: "潜在顧客の詳細セグメント分析を実施します。企業規模、業界、利用目的別の分類と各セグメントのニーズ調査を行いますが、顧客調査データの入力が必要な状態です。",
                context_status: [
                  {
                    id: "ctx_survey_data",
                    name: "顧客調査データ",
                    type: "file" as const,
                    required: true,
                    status: "insufficient" as const,
                    description: "顧客セグメント分析に必要な調査データファイル（CSV形式）",
                    current_value: null,
                  },
                  {
                    id: "ctx_segmentation_criteria",
                    name: "セグメント化基準",
                    type: "text" as const,
                    required: true,
                    status: "sufficient" as const,
                    description: "顧客をセグメント化する際の基準定義",
                    current_value: "企業規模（従業員数）、業界、プロジェクト管理の用途",
                  },
                ],
                waiting_for: [
                  {
                    type: "context" as const,
                    description: "顧客調査データ（500件のアンケート結果）の入力待ち",
                    estimated_time: "3-5日",
                  },
                ],
                execution_log: [
                  "顧客セグメント分析エージェント初期化完了",
                  "セグメント化基準の定義完了",
                  "調査対象業界の選定完了: IT, コンサル, 製造業, 金融",
                  "顧客調査データの入力待機中...",
                  "⚠️ 調査データなしでは分析を進行できません",
                ],
                progress_percentage: 15,
              }
            
            case "agent_pricing_22222":
              return {
                description: "最適な価格戦略を立案します。競合分析と顧客分析の結果を統合し、フリーミアム、階層課金などの価格モデルを検討して具体的な価格設定を提案しますが、他のエージェントの完了を待っています。",
                context_status: [
                  {
                    id: "ctx_pricing_models",
                    name: "検討する価格モデル",
                    type: "selection" as const,
                    required: true,
                    status: "sufficient" as const,
                    description: "検討対象となる価格設定モデル",
                    current_value: "freemium, tiered, usage_based",
                  },
                  {
                    id: "ctx_competitor_data",
                    name: "競合価格データ",
                    type: "text" as const,
                    required: true,
                    status: "pending" as const,
                    description: "競合他社の価格情報（競合分析エージェントから取得）",
                    current_value: "競合分析エージェントからの入力待ち",
                  },
                  {
                    id: "ctx_customer_willingness",
                    name: "顧客支払意向",
                    type: "text" as const,
                    required: true,
                    status: "insufficient" as const,
                    description: "顧客の支払意向価格データ（顧客分析エージェントから取得）",
                    current_value: "顧客分析エージェントからの入力待ち",
                  },
                ],
                waiting_for: [
                  {
                    type: "dependency" as const,
                    description: "競合分析エージェントからの価格データ取得待ち",
                    estimated_time: "5-7日",
                    dependencies: ["競合他社分析"],
                  },
                  {
                    type: "dependency" as const,
                    description: "顧客分析エージェントからの支払意向データ取得待ち",
                    estimated_time: "8-12日",
                    dependencies: ["顧客セグメント分析"],
                  },
                ],
                execution_log: [
                  "価格戦略エージェント初期化完了",
                  "価格モデル候補の定義完了",
                  "依存関係の確認: 競合分析・顧客分析の完了が必要",
                  "競合分析エージェントの進捗監視中 (60%完了)",
                  "顧客分析エージェントの実行開始待ち (データ不足)",
                  "⏳ 他エージェントの完了待機中...",
                ],
                progress_percentage: 10,
              }
            
            default:
              return {
                description: `${agent.purpose}に関する詳細な処理を実行します。`,
                context_status: mockContextStatus,
                waiting_for: [],
                execution_log: ["エージェント初期化完了"],
                progress_percentage: Math.floor(Math.random() * 100),
              }
          }
        }

        const specificData = getAgentSpecificData()

        return {
          agent_id: agent.agent_id,
          purpose: agent.purpose,
          description: specificData.description,
          level: agent.level,
          context_status: specificData.context_status,
          waiting_for: specificData.waiting_for,
          execution_log: specificData.execution_log,
          progress_percentage: specificData.progress_percentage,
          conversation_history: [],
          parent_agent_summary: agent.parent_agent_id 
            ? (() => {
                const parentAgent = agents.find((a) => a.agent_id === agent.parent_agent_id)
                return parentAgent ? {
                  agent_id: parentAgent.agent_id,
                  purpose: parentAgent.purpose,
                  status: parentAgent.status,
                  level: parentAgent.level,
                } : null
              })()
            : null,
          child_agent_summaries: agents
            .filter((a) => a.parent_agent_id === agent.agent_id)
            .map((a) => ({
              agent_id: a.agent_id,
              purpose: a.purpose,
              status: a.status,
              level: a.level,
            })),
        }
      } catch (error) {
        console.error("Failed to fetch agent meta info:", error)
        return null
      }
    },
    [agents],
  )

  const updateContext = useCallback(
    async (agentId: string, contextId: string, value: any): Promise<boolean> => {
      try {
        // TODO: Replace with actual API call to backend
        // const response = await fetch(`/api/agents/${agentId}/context`, {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({ contextId, value })
        // })
        // return response.ok

        // Mock implementation for demonstration
        console.log("Context update:", { agentId, contextId, value })
        return true
      } catch (error) {
        console.error("Failed to update context:", error)
        return false
      }
    },
    [],
  )

  const refreshAgentStatus = useCallback(
    async (agentId: string): Promise<void> => {
      try {
        // TODO: Replace with actual API call to backend
        // const response = await fetch(`/api/agents/${agentId}/status`)
        // const data = await response.json()
        // updateAgentStatus(agentId, data.status)

        // Mock implementation for demonstration
        console.log("Refreshing agent status:", agentId)
      } catch (error) {
        console.error("Failed to refresh agent status:", error)
      }
    },
    [],
  )

  return {
    agents,
    createAgent,
    createAgentFromTemplate,
    updateAgentStatus,
    executeAgent,
    completeAgent,
    fetchAgentMetaInfo,
    updateContext,
    refreshAgentStatus,
  }
}
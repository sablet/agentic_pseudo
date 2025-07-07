"use client"

import { useState } from "react"
import { useAgentManager } from "@/hooks/useAgentManager"
import { AgentList } from "@/components/agent-list"
import { AgentConversation } from "@/components/agent-conversation"
import { AgentInfoPanel } from "@/components/agent-info-panel"
import { AgentTemplateEditor } from "@/components/agent-template-editor"
import { DataUnitManager } from "@/components/data-unit-manager"
import { TemplateGallery } from "@/components/template-gallery"
import { Button } from "@/components/ui/button"
import { Settings } from "lucide-react"
import type { AgentMetaInfo, ContextStatus, WaitingInfo, ConversationMessage, AgentTemplate } from "@/types/agent"

export default function AgentCommunicationSystem() {
  const {
    agents,
    createAgent,
    createAgentWithTemplate,
    executeAgent,
    completeAgent,
    fetchAgentMetaInfo,
    updateContext,
    templates,
    saveTemplate,
    updateTemplate,
    deleteTemplate,
    getTemplate,
    getAgentTemplate,
  } = useAgentManager()
  
  // TODO: Add category definitions hook for real data
  // const { categoryDefinitions } = useCategoryDefinitions()
  
  // TODO: Fetch category definitions from backend
  // const fetchCategoryDefinitions = async (): Promise<DataUnitCategoryInfo[]> => {
  //   const response = await fetch('/api/data-unit-categories')
  //   return response.json()
  // }
  
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null)
  const [isTemplateGalleryOpen, setIsTemplateGalleryOpen] = useState(false)
  const [isDataUnitManagerOpen, setIsDataUnitManagerOpen] = useState(false)
  const [conversationHistory, setConversationHistory] = useState<ConversationMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<any>(null)
  const [isTemplateCreatorOpen, setIsTemplateCreatorOpen] = useState(false)

  const selectedAgent = selectedAgentId 
    ? agents.find((agent) => agent.agent_id === selectedAgentId) || null
    : null

  const handleSelectAgent = (agentId: string) => {
    setSelectedAgentId(agentId)
    
    // Load specific conversation history based on agent
    const getAgentConversation = () => {
      switch (agentId) {
        case "agent_parent_12345":
          return [
            {
              id: "1",
              role: "agent" as const,
              content: "包括的分析エージェントです。新製品の市場投入戦略を策定します。現在、3つの専門エージェントに分析を委任しています。",
              timestamp: new Date(Date.now() - 3600000),
            },
            {
              id: "2",
              role: "user" as const,
              content: "分析の進捗状況を教えてください。",
              timestamp: new Date(Date.now() - 3300000),
            },
            {
              id: "3",
              role: "agent" as const,
              content: "以下の状況です：\n\n✅ 競合他社分析: 60%完了 (実行中)\n⚠️ 顧客セグメント分析: 15%完了 (調査データ待ち)\n⏳ 価格戦略立案: 10%完了 (他エージェント完了待ち)\n\n競合分析が最も進んでおり、顧客分析は調査データの入力が必要です。",
              timestamp: new Date(Date.now() - 3000000),
            },
          ]
        
        case "agent_competitor_67890":
          return [
            {
              id: "1",
              role: "agent" as const,
              content: "競合分析エージェントです。Asana、Trello、Monday.com、Notion、Clickupの5社を詳細分析中です。",
              timestamp: new Date(Date.now() - 2800000),
            },
            {
              id: "2",
              role: "user" as const,
              content: "どの競合の分析が完了していますか？",
              timestamp: new Date(Date.now() - 2500000),
            },
            {
              id: "3",
              role: "agent" as const,
              content: "現在の進捗：\n\n✅ Asana: 機能・価格分析完了\n✅ Trello: 機能・価格分析完了  \n🔄 Monday.com: 分析実行中\n⏳ Notion: 待機中\n⏳ Clickup: 待機中\n\nAsanaとTrelloの分析データは既に収集済みです。Monday.comの分析を完了次第、残り2社に進みます。",
              timestamp: new Date(Date.now() - 2200000),
            },
          ]
        
        case "agent_customer_11111":
          return [
            {
              id: "1",
              role: "agent" as const,
              content: "顧客分析エージェントです。潜在顧客を企業規模・業界・用途別にセグメント化して分析します。",
              timestamp: new Date(Date.now() - 2600000),
            },
            {
              id: "2",
              role: "user" as const,
              content: "なぜ入力待ち状態になっているのですか？",
              timestamp: new Date(Date.now() - 2300000),
            },
            {
              id: "3",
              role: "agent" as const,
              content: "顧客調査データ（500件のアンケート結果CSVファイル）が必要ですが、まだ提供されていません。\n\nセグメント化基準は定義済みですが、実際の顧客データなしでは分析を進められない状況です。データが提供され次第、すぐに分析を開始できます。",
              timestamp: new Date(Date.now() - 2000000),
            },
          ]
        
        case "agent_pricing_22222":
          return [
            {
              id: "1",
              role: "agent" as const,
              content: "価格戦略エージェントです。競合分析と顧客分析の結果を基に最適な価格設定を提案します。",
              timestamp: new Date(Date.now() - 2400000),
            },
            {
              id: "2",
              role: "user" as const,
              content: "いつ頃分析を開始できそうですか？",
              timestamp: new Date(Date.now() - 2100000),
            },
            {
              id: "3",
              role: "agent" as const,
              content: "依存関係があるため、以下の完了を待っています：\n\n🔄 競合分析 → あと5-7日で完了予定\n⚠️ 顧客分析 → 調査データ次第（8-12日予定）\n\n両方のデータが揃い次第、フリーミアム、階層課金、従量課金の3つのモデルで価格戦略を検討します。",
              timestamp: new Date(Date.now() - 1800000),
            },
          ]
        
        default:
          return [
            {
              id: "1",
              role: "agent" as const,
              content: "こんにちは！何かお手伝いできることはありますか？",
              timestamp: new Date(),
            },
          ]
      }
    }
    
    setConversationHistory(getAgentConversation())
  }

  const handleSendMessage = async (content: string) => {
    if (!selectedAgent) return

    // Add user message
    const userMessage: ConversationMessage = {
      id: `msg_${Date.now()}_user`,
      role: "user",
      content,
      timestamp: new Date(),
    }
    setConversationHistory((prev) => [...prev, userMessage])

    // Set loading state
    setIsLoading(true)

    // TODO: Send message to backend and get agent response
    setTimeout(() => {
      const agentResponse: ConversationMessage = {
        id: `msg_${Date.now()}_agent`,
        role: "agent",
        content: `「${content}」について承知いたしました。詳細な分析を行い、適切な回答を提供いたします。`,
        timestamp: new Date(),
      }
      setConversationHistory((prev) => [...prev, agentResponse])
      setIsLoading(false)
    }, 1500)
  }

  const handleExecuteAgent = (agentId: string) => {
    executeAgent(agentId)
    console.log("Agent executed:", agentId)
  }

  const handleCreateAgent = () => {
    setIsTemplateGalleryOpen(true)
  }

  const handleSelectTemplate = (template: AgentTemplate, agentName: string) => {
    // テンプレートの purpose_category を purpose として使用し、
    // context_categories を context として使用
    const newAgent = createAgentWithTemplate(
      agentName, // カスタム名前をpurposeとして使用
      template,
      template.context_categories, // template.context_categories を context として使用
      null, // parent_agent_id (トップレベルエージェント)
      template.parameters // テンプレートのパラメータ
    )
    
    console.log("Agent created from template:", {
      agent: newAgent,
      template: template,
      name: agentName
    })
    
    setIsTemplateGalleryOpen(false)
    // 新しく作成されたエージェントを選択
    setSelectedAgentId(newAgent.agent_id)
  }

  const handleEditTemplate = (template: any) => {
    setEditingTemplate(template)
    setIsTemplateCreatorOpen(true)
    setIsTemplateGalleryOpen(false)
    console.log("Edit template:", template)
  }

  const handleDeleteTemplate = (templateId: string) => {
    if (confirm("このテンプレートを削除しますか？")) {
      deleteTemplate(templateId)
    }
  }

  const handleSaveTemplate = (template: any) => {
    if (editingTemplate) {
      // 編集モード
      updateTemplate(editingTemplate.template_id, template)
      console.log("Template updated:", template)
    } else {
      // 新規作成モード（現在は使用されない）
      const savedTemplate = saveTemplate(template)
      console.log("Template saved:", savedTemplate)
    }
  }

  // Get current agent info for AgentInfoPanel
  const getCurrentAgentInfo = (): AgentMetaInfo | null => {
    if (!selectedAgent) return null

    // Basic info without mock context data
    return {
      agent_id: selectedAgent.agent_id,
      purpose: selectedAgent.purpose,
      description: `${selectedAgent.purpose}に関する詳細な処理を実行します。`,
      level: selectedAgent.level,
      context_status: [], // Empty - no mock context
      waiting_for: [],   // Empty - no mock waiting info
      execution_log: [
        "エージェント初期化完了",
      ],
      conversation_history: conversationHistory,
      parent_agent_summary: selectedAgent.parent_agent_id 
        ? {
            agent_id: selectedAgent.parent_agent_id,
            purpose: "親エージェントの概要",
            status: "doing",
            level: selectedAgent.level - 1,
          }
        : null,
      child_agent_summaries: agents
        .filter((agent) => agent.parent_agent_id === selectedAgent.agent_id)
        .map((agent) => ({
          agent_id: agent.agent_id,
          purpose: agent.purpose,
          status: agent.status,
          level: agent.level,
        })),
    }
  }

  const handleUpdateContext = (contextId: string, value: any) => {
    if (!selectedAgent) return
    updateContext(selectedAgent.agent_id, contextId, value)
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-4 py-2">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-900">
            エージェント管理システム
          </h1>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsDataUnitManagerOpen(true)}
          >
            <Settings className="h-4 w-4 mr-2" />
            データユニット管理
          </Button>
        </div>
      </div>

      <div className="h-screen flex">
        {/* 左パネル: AgentList */}
        <div className="w-1/3 min-w-80 border-r border-slate-200">
          <AgentList
            agents={agents}
            selectedAgentId={selectedAgentId}
            onSelectAgent={handleSelectAgent}
            onExecuteAgent={handleExecuteAgent}
            onCreateAgent={handleCreateAgent}
          />
        </div>

        {/* 中央パネル: AgentConversation */}
        <div className="flex-1 min-w-0">
          <AgentConversation
            agent={selectedAgent}
            conversationHistory={conversationHistory}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>

        {/* 右パネル: AgentInfoPanel */}
        <div className="w-1/3 min-w-80 border-l border-slate-200">
          <AgentInfoPanel
            agentInfo={getCurrentAgentInfo()}
            template={selectedAgent ? getAgentTemplate(selectedAgent) : null}
            categoryDefinitions={undefined} // TODO: Implement real category master data fetching
            onUpdateContext={handleUpdateContext}
            onExecuteAgent={handleExecuteAgent}
            onApproveAgent={(agentId) => console.log("Approve agent:", agentId)}
          />
        </div>
      </div>

      <TemplateGallery
        isOpen={isTemplateGalleryOpen}
        onClose={() => setIsTemplateGalleryOpen(false)}
        templates={templates}
        onSelectTemplate={handleSelectTemplate}
        onDeleteTemplate={handleDeleteTemplate}
        onEditTemplate={handleEditTemplate}
      />

      {editingTemplate && (
        <AgentTemplateEditor
          isOpen={isTemplateCreatorOpen}
          onClose={() => {
            setIsTemplateCreatorOpen(false)
            setEditingTemplate(null)
          }}
          onSaveTemplate={handleSaveTemplate}
          editingTemplate={editingTemplate}
        />
      )}

      {isDataUnitManagerOpen && (
        <DataUnitManager
          onClose={() => setIsDataUnitManagerOpen(false)}
        />
      )}
    </div>
  )
}
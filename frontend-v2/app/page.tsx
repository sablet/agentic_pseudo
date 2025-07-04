"use client"

import { useState } from "react"
import { useAgentManager } from "@/hooks/useAgentManager"
import { ChatInterface } from "@/components/chat-interface"
import { Sidebar } from "@/components/sidebar"
import { AgentSettings } from "@/components/agent-settings"

export default function AgentCommunicationSystem() {
  const {
    agents,
    chatSessions,
    activeSessionId,
    setActiveSessionId,
    getActiveSession,
    createAgent,
    createAgentFromTemplate,
    executeAgent,
    completeAgent,
    addMessage,
    addSystemNotification,
  } = useAgentManager()
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)

  const handleSendMessage = (content: string) => {
    // ユーザーメッセージを追加
    addMessage({
      role: "user",
      content,
    })

    // AIの応答をシミュレート
    setTimeout(() => {
      const shouldProposeAgent = content.includes("エージェント") || content.includes("委任") || Math.random() > 0.7

      if (shouldProposeAgent) {
        addMessage({
          role: "assistant",
          content: "この作業は専門的なエージェントに委任することをお勧めします。以下のエージェントを生成しますか？",
          agent_proposal: {
            purpose: `${content}に関する情報収集と分析`,
            delegation_type: "information_gathering",
            context: `ユーザーからの要求: "${content}"に基づいて、関連する情報を収集し、分析結果を提供する。`,
            delegation_params: {
              search_keywords: content.split(" ").slice(0, 3),
              analysis_depth: "detailed",
            },
          },
        })
      } else {
        addMessage({
          role: "assistant",
          content: `「${content}」について承知いたしました。この内容について詳しく分析したい場合は、専門のエージェントを生成することも可能です。`,
        })
      }
    }, 1000)
  }

  const handleApproveAgent = (proposal: any) => {
    const newAgent = createAgent(
      proposal.purpose,
      proposal.delegation_type,
      proposal.context,
      null,
      proposal.delegation_params,
    )

    addSystemNotification(
      `新しいエージェント「${proposal.purpose}」が生成されました。サイドメニューから実行を開始できます。`,
      null,
    )
  }

  const handleExecuteAgent = (agentId: string) => {
    executeAgent(agentId)
    addSystemNotification(`エージェント（ID: ${agentId.slice(-8)}）の実行を開始しました。`, null)
  }

  const handleCompleteAgent = (agentId: string) => {
    completeAgent(agentId)
    addSystemNotification(`エージェント（ID: ${agentId.slice(-8)}）が完了しました。`, null)
  }

  const handleCreateAgentFromTemplate = (template: any) => {
    const newAgent = createAgentFromTemplate(template)
    addSystemNotification(
      `テンプレート「${template.name}」からエージェントが生成されました。サイドメニューから実行を開始できます。`,
      null,
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar
        agents={agents}
        chatSessions={chatSessions}
        activeSessionId={activeSessionId}
        onExecuteAgent={handleExecuteAgent}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onSelectSession={setActiveSessionId}
      />

      <div className="pl-4 pr-4 py-6">
        <div className="max-w-6xl mx-auto">
          <ChatInterface
            activeSession={getActiveSession()}
            agents={agents}
            onSendMessage={handleSendMessage}
            onApproveAgent={handleApproveAgent}
            onCompleteAgent={handleCompleteAgent}
          />
        </div>
      </div>

      <AgentSettings
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onCreateAgent={handleCreateAgentFromTemplate}
      />
    </div>
  )
}

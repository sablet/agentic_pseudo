"use client"

import { useState, useCallback } from "react"
import type { AgentInfo, ChatMessage, ChatSession } from "@/types/agent"

interface AgentTemplate {
  name: string
  delegation_type: string
  description: string
  default_context: string
  parameters: Record<string, any>
}

export function useAgentManager() {
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([
    {
      agent_id: null,
      agent_name: "メインチャット",
      messages: [
        {
          id: "1",
          role: "system_notification",
          content:
            "エージェント間情報受け渡しシステムへようこそ。新しいエージェントの生成や既存エージェントの管理を行えます。",
          timestamp: new Date(),
        },
      ],
    },
  ])
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null)

  const generateAgentId = useCallback(() => {
    return `agent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }, [])

  const getActiveSession = useCallback(() => {
    return chatSessions.find((session) => session.agent_id === activeSessionId) || chatSessions[0]
  }, [chatSessions, activeSessionId])

  const createAgent = useCallback(
    (
      purpose: string,
      delegation_type: string,
      context: string,
      parent_agent_id: string | null = null,
      delegation_params?: Record<string, any>,
    ) => {
      const newAgent: AgentInfo = {
        agent_id: generateAgentId(),
        parent_agent_id,
        purpose,
        context,
        delegation_type,
        status: "pending",
        delegation_params,
        created_at: new Date(),
        updated_at: new Date(),
      }

      setAgents((prev) => [...prev, newAgent])

      // 新しいエージェント用のチャットセッションを作成
      const newSession: ChatSession = {
        agent_id: newAgent.agent_id,
        agent_name: purpose.length > 20 ? purpose.slice(0, 20) + "..." : purpose,
        messages: [
          {
            id: `msg_${Date.now()}`,
            role: "system_notification",
            content: `エージェント「${purpose}」のチャットセッションが作成されました。`,
            timestamp: new Date(),
            agent_id: newAgent.agent_id,
          },
        ],
      }

      setChatSessions((prev) => [...prev, newSession])

      return newAgent
    },
    [generateAgentId],
  )

  const createAgentFromTemplate = useCallback(
    (template: AgentTemplate, customPurpose?: string, customContext?: string) => {
      const purpose = customPurpose || `${template.name}による処理`
      const context = customContext || template.default_context

      return createAgent(purpose, template.delegation_type, context, null, template.parameters)
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
      updateAgentStatus(agent_id, "in_progress")

      const agent = agents.find((a) => a.agent_id === agent_id)
      if (agent) {
        // エージェントのセッションにメッセージを追加
        setChatSessions((prev) =>
          prev.map((session) =>
            session.agent_id === agent_id
              ? {
                  ...session,
                  messages: [
                    ...session.messages,
                    {
                      id: `msg_${Date.now()}`,
                      role: "system_notification",
                      content: `エージェントの実行を開始しました。`,
                      timestamp: new Date(),
                      agent_id,
                    },
                  ],
                }
              : session,
          ),
        )
      }
    },
    [agents, updateAgentStatus],
  )

  const completeAgent = useCallback(
    (agent_id: string) => {
      updateAgentStatus(agent_id, "completed")

      const agent = agents.find((a) => a.agent_id === agent_id)
      if (agent) {
        setChatSessions((prev) =>
          prev.map((session) =>
            session.agent_id === agent_id
              ? {
                  ...session,
                  messages: [
                    ...session.messages,
                    {
                      id: `msg_${Date.now()}`,
                      role: "system_notification",
                      content: `エージェントが完了しました。`,
                      timestamp: new Date(),
                      agent_id,
                    },
                  ],
                }
              : session,
          ),
        )
      }
    },
    [agents, updateAgentStatus],
  )

  const addMessage = useCallback(
    (message: Omit<ChatMessage, "id" | "timestamp">, sessionId?: string | null) => {
      const targetSessionId = sessionId !== undefined ? sessionId : activeSessionId
      const newMessage: ChatMessage = {
        ...message,
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date(),
        agent_id: targetSessionId,
      }

      setChatSessions((prev) =>
        prev.map((session) =>
          session.agent_id === targetSessionId ? { ...session, messages: [...session.messages, newMessage] } : session,
        ),
      )
    },
    [activeSessionId],
  )

  const addSystemNotification = useCallback(
    (content: string, sessionId?: string | null) => {
      addMessage(
        {
          role: "system_notification",
          content,
        },
        sessionId,
      )
    },
    [addMessage],
  )

  return {
    agents,
    chatSessions,
    activeSessionId,
    setActiveSessionId,
    getActiveSession,
    createAgent,
    createAgentFromTemplate,
    updateAgentStatus,
    executeAgent,
    completeAgent,
    addMessage,
    addSystemNotification,
  }
}

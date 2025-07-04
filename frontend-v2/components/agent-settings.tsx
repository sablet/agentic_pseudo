"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Plus, Trash2, Edit } from "lucide-react"

interface AgentTemplate {
  id: string
  name: string
  delegation_type: string
  description: string
  default_context: string
  parameters: Record<string, any>
}

interface AgentSettingsProps {
  isOpen: boolean
  onClose: () => void
  onCreateAgent: (template: Omit<AgentTemplate, "id">) => void
}

export function AgentSettings({ isOpen, onClose, onCreateAgent }: AgentSettingsProps) {
  const [templates, setTemplates] = useState<AgentTemplate[]>([
    {
      id: "1",
      name: "情報収集エージェント",
      delegation_type: "information_gathering",
      description: "指定されたトピックについて情報を収集し、整理して報告します",
      default_context: "以下のトピックについて詳細な情報を収集してください：",
      parameters: {
        search_depth: "detailed",
        source_types: ["web", "academic", "news"],
        max_results: 10,
      },
    },
    {
      id: "2",
      name: "分析エージェント",
      delegation_type: "analysis",
      description: "データや情報を分析し、洞察を提供します",
      default_context: "以下のデータを分析し、重要な洞察を抽出してください：",
      parameters: {
        analysis_type: "comprehensive",
        include_charts: true,
        confidence_threshold: 0.8,
      },
    },
    {
      id: "3",
      name: "要約エージェント",
      delegation_type: "summarization",
      description: "長い文書や情報を簡潔に要約します",
      default_context: "以下の内容を要約してください：",
      parameters: {
        summary_length: "medium",
        include_key_points: true,
        format: "bullet_points",
      },
    },
  ])

  const [showForm, setShowForm] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<AgentTemplate | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    delegation_type: "",
    description: "",
    default_context: "",
    parameters: "{}",
  })

  const resetForm = () => {
    setFormData({
      name: "",
      delegation_type: "",
      description: "",
      default_context: "",
      parameters: "{}",
    })
    setEditingTemplate(null)
    setShowForm(false)
  }

  const handleCreateTemplate = () => {
    setFormData({
      name: "",
      delegation_type: "",
      description: "",
      default_context: "",
      parameters: "{}",
    })
    setEditingTemplate(null)
    setShowForm(true)
  }

  const handleEditTemplate = (template: AgentTemplate) => {
    setEditingTemplate(template)
    setFormData({
      name: template.name,
      delegation_type: template.delegation_type,
      description: template.description,
      default_context: template.default_context,
      parameters: JSON.stringify(template.parameters, null, 2),
    })
    setShowForm(true)
  }

  const handleSaveTemplate = () => {
    if (!formData.name || !formData.delegation_type || !formData.description) {
      alert("必須項目を入力してください")
      return
    }

    try {
      const parameters = JSON.parse(formData.parameters)
      const templateData = {
        name: formData.name,
        delegation_type: formData.delegation_type,
        description: formData.description,
        default_context: formData.default_context,
        parameters,
      }

      if (editingTemplate) {
        setTemplates((prev) =>
          prev.map((t) => (t.id === editingTemplate.id ? { ...templateData, id: editingTemplate.id } : t)),
        )
      } else {
        const newTemplate = {
          ...templateData,
          id: Date.now().toString(),
        }
        setTemplates((prev) => [...prev, newTemplate])
      }

      resetForm()
    } catch (error) {
      alert("パラメータのJSON形式が正しくありません")
    }
  }

  const handleDeleteTemplate = (id: string) => {
    if (confirm("このテンプレートを削除しますか？")) {
      setTemplates((prev) => prev.filter((t) => t.id !== id))
    }
  }

  const handleUseTemplate = (template: AgentTemplate) => {
    onCreateAgent({
      name: template.name,
      delegation_type: template.delegation_type,
      description: template.description,
      default_context: template.default_context,
      parameters: template.parameters,
    })
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
          {/* テンプレート一覧 */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">エージェントテンプレート</h3>
              <Button onClick={handleCreateTemplate} size="sm">
                <Plus className="h-4 w-4 mr-1" />
                新規作成
              </Button>
            </div>

            <ScrollArea className="h-[500px]">
              <div className="space-y-3">
                {templates.map((template) => (
                  <Card key={template.id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-sm">{template.name}</CardTitle>
                          <Badge variant="outline" className="mt-1">
                            {template.delegation_type}
                          </Badge>
                        </div>
                        <div className="flex gap-1">
                          <Button variant="outline" size="sm" onClick={() => handleEditTemplate(template)}>
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteTemplate(template.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <p className="text-xs text-gray-600 mb-3">{template.description}</p>
                      <Button size="sm" onClick={() => handleUseTemplate(template)} className="w-full">
                        このテンプレートを使用
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </div>

          {/* テンプレート作成・編集フォーム */}
          {showForm && (
            <div>
              <h3 className="text-lg font-medium mb-4">
                {editingTemplate ? "テンプレート編集" : "新規テンプレート作成"}
              </h3>

              <ScrollArea className="h-[500px]">
                <div className="space-y-4 pr-4">
                  <div>
                    <Label htmlFor="name">テンプレート名 *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                      placeholder="例: 情報収集エージェント"
                    />
                  </div>

                  <div>
                    <Label htmlFor="delegation_type">委任タイプ *</Label>
                    <Select
                      value={formData.delegation_type}
                      onValueChange={(value) => setFormData((prev) => ({ ...prev, delegation_type: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="委任タイプを選択" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="information_gathering">情報収集</SelectItem>
                        <SelectItem value="analysis">分析</SelectItem>
                        <SelectItem value="summarization">要約</SelectItem>
                        <SelectItem value="planning">計画立案</SelectItem>
                        <SelectItem value="human_escalation">人間エスカレーション</SelectItem>
                        <SelectItem value="custom">カスタム</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="description">説明 *</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                      placeholder="このエージェントの役割と機能を説明してください"
                      rows={3}
                    />
                  </div>

                  <div>
                    <Label htmlFor="default_context">デフォルトコンテキスト</Label>
                    <Textarea
                      id="default_context"
                      value={formData.default_context}
                      onChange={(e) => setFormData((prev) => ({ ...prev, default_context: e.target.value }))}
                      placeholder="エージェントに渡されるデフォルトの指示やコンテキスト"
                      rows={3}
                    />
                  </div>

                  <div>
                    <Label htmlFor="parameters">パラメータ (JSON)</Label>
                    <Textarea
                      id="parameters"
                      value={formData.parameters}
                      onChange={(e) => setFormData((prev) => ({ ...prev, parameters: e.target.value }))}
                      placeholder='{"key": "value"}'
                      rows={4}
                      className="font-mono text-sm"
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button onClick={handleSaveTemplate} className="flex-1">
                      {editingTemplate ? "更新" : "作成"}
                    </Button>
                    <Button variant="outline" onClick={resetForm} className="flex-1 bg-transparent">
                      キャンセル
                    </Button>
                  </div>
                </div>
              </ScrollArea>
            </div>
          )}

          {/* フォームが表示されていない時の説明 */}
          {!showForm && (
            <div className="flex items-center justify-center h-[500px] text-center">
              <div className="text-gray-500">
                <p className="mb-2">新規作成ボタンでテンプレートを作成</p>
                <p>編集ボタンで既存テンプレートを修正できます</p>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

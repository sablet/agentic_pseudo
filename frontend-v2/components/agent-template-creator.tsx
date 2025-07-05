"use client"

import React, { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { DataUnitSelector } from "@/components/data-unit-selector"
import { 
  Plus, 
  X, 
  Target, 
  FileText,
  Save,
  Cpu
} from "lucide-react"
import type { DataUnitCategory, ExecutionEngine, AgentTemplate } from "@/types/agent"


interface AgentTemplateCreatorProps {
  isOpen: boolean
  onClose: () => void
  onSaveTemplate: (template: Omit<AgentTemplate, 'template_id' | 'created_at' | 'updated_at' | 'usage_count'>) => void
  onCreateAgent: (template: AgentTemplate) => void
}

export function AgentTemplateCreator({
  isOpen,
  onClose,
  onSaveTemplate,
  onCreateAgent,
}: AgentTemplateCreatorProps) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    delegation_type: "",
    purpose_category: "" as DataUnitCategory,
    context_categories: [] as DataUnitCategory[],
    execution_engine: "gemini-2.5-flash" as ExecutionEngine,
    parameters: "{}",
  })

  const resetForm = () => {
    setFormData({
      name: "",
      description: "",
      delegation_type: "",
      purpose_category: "" as DataUnitCategory,
      context_categories: [] as DataUnitCategory[],
      execution_engine: "gemini-2.5-flash" as ExecutionEngine,
      parameters: "{}",
    })
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  const handleAddContext = () => {
    setFormData((prev) => ({
      ...prev,
      context_categories: [...prev.context_categories, "" as DataUnitCategory],
    }))
  }

  const handleRemoveContext = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      context_categories: prev.context_categories.filter((_, i) => i !== index),
    }))
  }

  const handleContextChange = (index: number, value: DataUnitCategory) => {
    setFormData((prev) => ({
      ...prev,
      context_categories: prev.context_categories.map((item, i) => 
        i === index ? value : item
      ),
    }))
  }

  const handleSaveTemplate = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name || !formData.delegation_type || !formData.purpose_category || formData.context_categories.length === 0) {
      console.error("テンプレート名、委任タイプ、目的、コンテキストは必須項目です")
      return
    }

    const filteredContexts = formData.context_categories.filter(context => context.trim() !== "")
    
    try {
      const parameters = JSON.parse(formData.parameters)
      const template = {
        name: formData.name,
        description: formData.description,
        delegation_type: formData.delegation_type,
        purpose_category: formData.purpose_category,
        context_categories: filteredContexts,
        execution_engine: formData.execution_engine,
        parameters,
      }

      onSaveTemplate(template)
      handleClose()
    } catch (error) {
      console.error("パラメータのJSON形式が正しくありません")
    }
  }

  const handleCreateAgent = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name || !formData.delegation_type || !formData.purpose_category || formData.context_categories.length === 0) {
      console.error("テンプレート名、委任タイプ、目的、コンテキストは必須項目です")
      return
    }

    const filteredContexts = formData.context_categories.filter(context => context.trim() !== "")
    
    try {
      const parameters = JSON.parse(formData.parameters)
      const template: AgentTemplate = {
        template_id: `temp_${Date.now()}`,
        name: formData.name,
        description: formData.description,
        delegation_type: formData.delegation_type,
        purpose_category: formData.purpose_category,
        context_categories: filteredContexts,
        execution_engine: formData.execution_engine,
        parameters,
        created_at: new Date(),
        updated_at: new Date(),
        usage_count: 0,
      }

      onCreateAgent(template)
      handleClose()
    } catch (error) {
      console.error("パラメータのJSON形式が正しくありません")
    }
  }

  // Sample delegation types for suggestions
  const commonDelegationTypes = [
    "データ分析",
    "コンテンツ作成",
    "リサーチ",
    "競合分析",
    "顧客分析",
    "市場調査",
    "技術レビュー",
    "品質保証",
    "企画立案",
    "レポート作成",
  ]

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            新しいエージェントテンプレート作成
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="max-h-[70vh] pr-4">
          <form className="space-y-6 mt-4">
            {/* テンプレート名 */}
            <div>
              <Label htmlFor="name" className="text-sm font-medium">
                テンプレート名 <span className="text-red-500">*</span>
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                placeholder="例: 競合分析テンプレート"
                className="mt-1"
              />
              <p className="text-xs text-slate-500 mt-1">
                このテンプレートを識別するための名前を入力してください
              </p>
            </div>

            {/* テンプレート説明 */}
            <div>
              <Label htmlFor="description" className="text-sm font-medium">
                説明
              </Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                placeholder="このテンプレートの用途や特徴を説明してください"
                rows={3}
                className="mt-1"
              />
              <p className="text-xs text-slate-500 mt-1">
                他のユーザーがテンプレートを理解できるよう詳細を記述してください
              </p>
            </div>

            {/* 委任タイプ（表示名） */}
            <div>
              <Label htmlFor="delegation_type" className="text-sm font-medium">
                委任タイプ（表示名） <span className="text-red-500">*</span>
              </Label>
              <Input
                id="delegation_type"
                value={formData.delegation_type}
                onChange={(e) => setFormData((prev) => ({ ...prev, delegation_type: e.target.value }))}
                placeholder="例: 競合分析"
                className="mt-1"
              />
              <div className="mt-2 flex flex-wrap gap-1">
                <p className="text-xs text-slate-500 w-full mb-1">よく使われるタイプ:</p>
                {commonDelegationTypes.slice(0, 6).map((type) => (
                  <Badge
                    key={type}
                    variant="outline"
                    className="text-xs cursor-pointer hover:bg-slate-100"
                    onClick={() => setFormData((prev) => ({ ...prev, delegation_type: type }))}
                  >
                    {type}
                  </Badge>
                ))}
              </div>
            </div>

            {/* 目的（DataUnit） */}
            <div>
              <DataUnitSelector
                value={formData.purpose_category}
                onChange={(value) => setFormData((prev) => ({ ...prev, purpose_category: value }))}
                label="目的カテゴリ"
                placeholder="このエージェントが生成するデータユニットカテゴリを選択"
                required={true}
              />
              <p className="text-xs text-slate-500 mt-1">
                このエージェントが生成する成果物の種類を選択してください
              </p>
            </div>

            {/* コンテキスト（DataUnit配列） */}
            <div>
              <Label className="text-sm font-medium flex items-center gap-2">
                <FileText className="h-4 w-4" />
                コンテキスト <span className="text-red-500">*</span>
              </Label>
              <p className="text-xs text-slate-500 mt-1 mb-3">
                このエージェントが作業に必要とする入力データの種類を選択してください
              </p>
              
              <div className="space-y-2">
                {formData.context_categories.length === 0 ? (
                  <div className="text-center py-4 border-2 border-dashed border-slate-300 rounded-lg">
                    <p className="text-sm text-slate-500 mb-2">コンテキストが設定されていません</p>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleAddContext}
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      コンテキストを追加
                    </Button>
                  </div>
                ) : (
                  <>
                    {formData.context_categories.map((contextItem, index) => (
                      <div key={index} className="flex gap-2">
                        <div className="flex-1">
                          <DataUnitSelector
                            value={contextItem}
                            onChange={(value) => handleContextChange(index, value)}
                            placeholder="コンテキストを選択"
                            required={true}
                          />
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          size="icon"
                          onClick={() => handleRemoveContext(index)}
                          className="flex-shrink-0"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                    
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleAddContext}
                      className="w-full"
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      コンテキストを追加
                    </Button>
                  </>
                )}
              </div>
            </div>

            {/* 実行エンジン */}
            <div>
              <Label className="text-sm font-medium flex items-center gap-2">
                <Cpu className="h-4 w-4" />
                実行エンジン <span className="text-red-500">*</span>
              </Label>
              <Select
                value={formData.execution_engine}
                onValueChange={(value: ExecutionEngine) => setFormData((prev) => ({ ...prev, execution_engine: value }))}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="実行エンジンを選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gemini-2.5-flash">Gemini 2.5 Flash</SelectItem>
                  <SelectItem value="claude-code">Claude Code</SelectItem>
                  <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                  <SelectItem value="gpt-4o-mini">GPT-4o Mini</SelectItem>
                  <SelectItem value="claude-3.5-sonnet">Claude 3.5 Sonnet</SelectItem>
                  <SelectItem value="gemini-1.5-pro">Gemini 1.5 Pro</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-slate-500 mt-1">
                このエージェントを実行するAIエンジンを選択してください
              </p>
            </div>


            {/* パラメータ */}
            <div>
              <Label htmlFor="parameters" className="text-sm font-medium">
                追加パラメータ (JSON)
              </Label>
              <Textarea
                id="parameters"
                value={formData.parameters}
                onChange={(e) => setFormData((prev) => ({ ...prev, parameters: e.target.value }))}
                placeholder='{"option1": "value1", "option2": "value2"}'
                rows={4}
                className="mt-1 font-mono text-sm"
              />
              <p className="text-xs text-slate-500 mt-1">
                エージェント実行時に使用する追加設定をJSON形式で入力
              </p>
            </div>

            {/* プレビュー */}
            {formData.name && formData.delegation_type && formData.purpose_category && formData.context_categories && (
              <Card className="bg-slate-50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">プレビュー</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2 text-sm">
                    <p><strong>テンプレート名:</strong> {formData.name}</p>
                    {formData.description && (
                      <p><strong>説明:</strong> {formData.description}</p>
                    )}
                    <p><strong>委任タイプ:</strong> {formData.delegation_type}</p>
                    <p><strong>目的:</strong> {formData.purpose_category}</p>
                    <div>
                      <strong>コンテキスト:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {formData.context_categories.map((contextItem, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {contextItem}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <p><strong>実行エンジン:</strong> {formData.execution_engine}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* ボタン */}
            <div className="flex gap-2 pt-4">
              <Button 
                type="button"
                onClick={handleSaveTemplate}
                className="flex-1 bg-green-600 hover:bg-green-700"
              >
                <Save className="h-4 w-4 mr-2" />
                テンプレートを保存
              </Button>
              <Button 
                type="button"
                onClick={handleCreateAgent}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
              >
                <Target className="h-4 w-4 mr-2" />
                エージェントを作成
              </Button>
              <Button type="button" variant="outline" onClick={handleClose} className="flex-1">
                キャンセル
              </Button>
            </div>
          </form>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
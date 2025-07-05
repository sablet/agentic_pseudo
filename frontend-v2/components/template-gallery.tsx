"use client"

import React, { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Search, 
  BookTemplate, 
  Star, 
  Clock, 
  Target, 
  FileText,
  Trash2,
  Edit,
  Calendar,
  TrendingUp
} from "lucide-react"
import type { AgentTemplate } from "@/types/agent"

interface TemplateGalleryProps {
  isOpen: boolean
  onClose: () => void
  templates: AgentTemplate[]
  onSelectTemplate: (template: AgentTemplate) => void
  onDeleteTemplate: (templateId: string) => void
  onEditTemplate: (template: AgentTemplate) => void
}

export function TemplateGallery({
  isOpen,
  onClose,
  templates,
  onSelectTemplate,
  onDeleteTemplate,
  onEditTemplate,
}: TemplateGalleryProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedTemplate, setSelectedTemplate] = useState<AgentTemplate | null>(null)

  const filteredTemplates = templates.filter(template =>
    template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    template.delegation_type.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleSelectTemplate = (template: AgentTemplate) => {
    setSelectedTemplate(template)
  }

  const handleConfirmSelection = () => {
    if (selectedTemplate) {
      onSelectTemplate(selectedTemplate)
      onClose()
    }
  }

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BookTemplate className="h-5 w-5" />
            テンプレートギャラリー
          </DialogTitle>
        </DialogHeader>

        <div className="flex flex-col space-y-4">
          {/* 検索バー */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="テンプレートを検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* テンプレート一覧 */}
          <div className="flex gap-4 h-[60vh]">
            {/* 左側: テンプレート一覧 */}
            <div className="flex-1">
              <ScrollArea className="h-full">
                <div className="grid gap-3">
                  {filteredTemplates.length === 0 ? (
                    <div className="text-center py-8 text-slate-500">
                      <BookTemplate className="h-12 w-12 mx-auto mb-4 text-slate-300" />
                      <p className="text-lg font-medium">テンプレートがありません</p>
                      <p className="text-sm">新しいテンプレートを作成してください</p>
                    </div>
                  ) : (
                    filteredTemplates.map((template) => (
                      <Card
                        key={template.template_id}
                        className={`cursor-pointer transition-all hover:shadow-md ${
                          selectedTemplate?.template_id === template.template_id
                            ? "ring-2 ring-blue-500 bg-blue-50"
                            : ""
                        }`}
                        onClick={() => handleSelectTemplate(template)}
                      >
                        <CardHeader className="pb-2">
                          <div className="flex justify-between items-start">
                            <CardTitle className="text-sm font-medium">
                              {template.name}
                            </CardTitle>
                            <div className="flex gap-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  onEditTemplate(template)
                                }}
                                className="h-6 w-6 p-0"
                              >
                                <Edit className="h-3 w-3" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  onDeleteTemplate(template.template_id)
                                }}
                                className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent className="pt-0">
                          <div className="space-y-2">
                            <Badge variant="secondary" className="text-xs">
                              {template.delegation_type}
                            </Badge>
                            <p className="text-xs text-slate-600 line-clamp-2">
                              {template.description}
                            </p>
                            <div className="flex items-center gap-3 text-xs text-slate-500">
                              <div className="flex items-center gap-1">
                                <Calendar className="h-3 w-3" />
                                {formatDate(template.created_at)}
                              </div>
                              <div className="flex items-center gap-1">
                                <TrendingUp className="h-3 w-3" />
                                {template.usage_count}回使用
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </ScrollArea>
            </div>

            {/* 右側: テンプレート詳細 */}
            <div className="w-80">
              {selectedTemplate ? (
                <Card className="h-full">
                  <CardHeader>
                    <CardTitle className="text-sm">テンプレート詳細</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-96">
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-medium text-sm mb-1">テンプレート名</h4>
                          <p className="text-sm text-slate-600">{selectedTemplate.name}</p>
                        </div>
                        
                        {selectedTemplate.description && (
                          <div>
                            <h4 className="font-medium text-sm mb-1">説明</h4>
                            <p className="text-sm text-slate-600">{selectedTemplate.description}</p>
                          </div>
                        )}
                        
                        <div>
                          <h4 className="font-medium text-sm mb-1">委任タイプ</h4>
                          <Badge variant="outline">{selectedTemplate.delegation_type}</Badge>
                        </div>
                        
                        <div>
                          <h4 className="font-medium text-sm mb-1 flex items-center gap-1">
                            <Target className="h-3 w-3" />
                            目的
                          </h4>
                          <p className="text-sm text-slate-600">{selectedTemplate.purpose_category}</p>
                        </div>
                        
                        <div>
                          <h4 className="font-medium text-sm mb-1 flex items-center gap-1">
                            <FileText className="h-3 w-3" />
                            コンテキスト
                          </h4>
                          <div className="flex flex-wrap gap-1">
                            {selectedTemplate.context_categories.map((item, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {item}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="font-medium text-sm mb-1">実行エンジン</h4>
                          <p className="text-sm text-slate-600">{selectedTemplate.execution_engine}</p>
                        </div>
                        
                        <div>
                          <h4 className="font-medium text-sm mb-1 flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            作成日時
                          </h4>
                          <p className="text-sm text-slate-600">
                            {formatDate(selectedTemplate.created_at)}
                          </p>
                        </div>
                        
                        <div>
                          <h4 className="font-medium text-sm mb-1 flex items-center gap-1">
                            <Star className="h-3 w-3" />
                            使用回数
                          </h4>
                          <p className="text-sm text-slate-600">{selectedTemplate.usage_count}回</p>
                        </div>
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              ) : (
                <Card className="h-full flex items-center justify-center">
                  <CardContent className="text-center">
                    <BookTemplate className="h-12 w-12 mx-auto mb-4 text-slate-300" />
                    <p className="text-sm text-slate-500">
                      テンプレートを選択してください
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          {/* ボタン */}
          <div className="flex gap-3 pt-4">
            <Button
              onClick={handleConfirmSelection}
              disabled={!selectedTemplate}
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              <Target className="h-4 w-4 mr-2" />
              このテンプレートからエージェントを作成
            </Button>
            <Button variant="outline" onClick={onClose} className="flex-1">
              キャンセル
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
"use client"

import React, { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from "@/components/ui/command"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Check, ChevronDown, Plus } from "lucide-react"
import type { DataUnit } from "@/types/agent"

interface DataUnitSelectorProps {
  value: DataUnit
  onChange: (value: DataUnit) => void
  placeholder?: string
  label?: string
  required?: boolean
  disabled?: boolean
}

export function DataUnitSelector({
  value,
  onChange,
  placeholder = "データユニットを選択または入力",
  label,
  required = false,
  disabled = false,
}: DataUnitSelectorProps) {
  const [open, setOpen] = useState(false)
  const [isCustomInput, setIsCustomInput] = useState(false)
  const [customValue, setCustomValue] = useState("")

  // Predefined data units with Japanese labels
  const predefinedDataUnits: Array<{ value: DataUnit; label: string; category: string }> = [
    // Reports & Analysis
    { value: "market_analysis_report", label: "市場分析レポート", category: "レポート・分析" },
    { value: "competitor_comparison_table", label: "競合比較表", category: "レポート・分析" },
    { value: "customer_segment_data", label: "顧客セグメントデータ", category: "レポート・分析" },
    { value: "pricing_strategy_document", label: "価格戦略書", category: "レポート・分析" },
    { value: "risk_assessment_report", label: "リスク評価レポート", category: "レポート・分析" },
    { value: "performance_metrics", label: "パフォーマンス指標", category: "レポート・分析" },
    
    // Technical Documents
    { value: "technical_specifications", label: "技術仕様書", category: "技術文書" },
    { value: "feature_analysis_matrix", label: "機能分析マトリックス", category: "技術文書" },
    { value: "integration_requirements", label: "統合要件", category: "技術文書" },
    { value: "compliance_checklist", label: "コンプライアンスチェックリスト", category: "技術文書" },
    
    // Data & Research
    { value: "market_share_data", label: "市場シェアデータ", category: "データ・調査" },
    { value: "user_survey_results", label: "ユーザー調査結果", category: "データ・調査" },
    { value: "user_feedback_summary", label: "ユーザーフィードバック要約", category: "データ・調査" },
    { value: "financial_projections", label: "財務予測", category: "データ・調査" },
    
    // Training & Support
    { value: "training_materials", label: "研修資料", category: "研修・サポート" },
    
    // Business Documents
    { value: "business_requirements_document", label: "業務要件書", category: "ビジネス文書" },
  ]

  const groupedDataUnits = predefinedDataUnits.reduce((acc, item) => {
    if (!acc[item.category]) {
      acc[item.category] = []
    }
    acc[item.category].push(item)
    return acc
  }, {} as Record<string, typeof predefinedDataUnits>)

  const handleSelect = (selectedValue: DataUnit) => {
    onChange(selectedValue)
    setOpen(false)
  }

  const handleCustomSubmit = () => {
    if (customValue.trim()) {
      onChange(customValue.trim())
      setCustomValue("")
      setIsCustomInput(false)
      setOpen(false)
    }
  }

  const getDisplayLabel = (value: DataUnit): string => {
    const predefined = predefinedDataUnits.find(item => item.value === value)
    return predefined ? predefined.label : value
  }

  return (
    <div className="w-full">
      {label && (
        <Label className="text-sm font-medium mb-2 block">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
      )}
      
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between"
            disabled={disabled}
          >
            <span className="truncate">
              {value ? getDisplayLabel(value) : placeholder}
            </span>
            <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        
        <PopoverContent className="w-[400px] p-0" align="start">
          <Command>
            <CommandInput placeholder="データユニットを検索..." />
            <CommandEmpty>
              <div className="p-4 text-center">
                <p className="text-sm text-slate-500 mb-3">該当するデータユニットが見つかりません</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsCustomInput(true)}
                  className="w-full"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  カスタム値を入力
                </Button>
              </div>
            </CommandEmpty>
            
            <ScrollArea className="max-h-[300px]">
              {Object.entries(groupedDataUnits).map(([category, items]) => (
                <CommandGroup key={category} heading={category}>
                  {items.map((item) => (
                    <CommandItem
                      key={item.value}
                      onSelect={() => handleSelect(item.value)}
                      className="flex items-center justify-between"
                    >
                      <div className="flex items-center">
                        <Check
                          className={`mr-2 h-4 w-4 ${
                            value === item.value ? "opacity-100" : "opacity-0"
                          }`}
                        />
                        <div>
                          <div className="font-medium">{item.label}</div>
                          <div className="text-xs text-slate-500">{item.value}</div>
                        </div>
                      </div>
                    </CommandItem>
                  ))}
                </CommandGroup>
              ))}
            </ScrollArea>
            
            <div className="border-t p-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsCustomInput(true)}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                カスタム値を入力
              </Button>
            </div>
          </Command>
        </PopoverContent>
      </Popover>

      {/* Custom Input Modal */}
      {isCustomInput && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-[90vw]">
            <h3 className="text-lg font-semibold mb-4">カスタムデータユニット</h3>
            <div className="space-y-4">
              <div>
                <Label htmlFor="custom-input">データユニット名</Label>
                <Input
                  id="custom-input"
                  value={customValue}
                  onChange={(e) => setCustomValue(e.target.value)}
                  placeholder="例: custom_analysis_report"
                  className="mt-1"
                  autoFocus
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={handleCustomSubmit}
                  disabled={!customValue.trim()}
                  className="flex-1"
                >
                  追加
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsCustomInput(false)
                    setCustomValue("")
                  }}
                  className="flex-1"
                >
                  キャンセル
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
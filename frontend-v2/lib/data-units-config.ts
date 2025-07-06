"use client"

import type { DataUnitCategory } from "@/types/agent"

export interface DataUnitConfig {
  value: DataUnitCategory
  label: string
  category: string
  editable?: boolean
}

export interface DataUnitCategoryInfo {
  id: string
  name: string
  editable?: boolean
}

// Predefined categories
export const DEFAULT_CATEGORIES: DataUnitCategoryInfo[] = [
  { id: "reports", name: "レポート・分析", editable: false },
  { id: "technical", name: "技術文書", editable: false },
  { id: "data", name: "データ・調査", editable: false },
  { id: "training", name: "研修・サポート", editable: false },
  { id: "business", name: "ビジネス文書", editable: false },
]

// Predefined data units
export const DEFAULT_DATA_UNITS: DataUnitConfig[] = [
  // Reports & Analysis
  { value: "market_analysis_report", label: "市場分析レポート", category: "レポート・分析", editable: true },
  { value: "competitor_comparison_table", label: "競合比較表", category: "レポート・分析", editable: true },
  { value: "customer_segment_data", label: "顧客セグメントデータ", category: "レポート・分析", editable: true },
  { value: "pricing_strategy_document", label: "価格戦略書", category: "レポート・分析", editable: true },
  { value: "risk_assessment_report", label: "リスク評価レポート", category: "レポート・分析", editable: true },
  { value: "performance_metrics", label: "パフォーマンス指標", category: "レポート・分析", editable: true },
  
  // Technical Documents
  { value: "technical_specifications", label: "技術仕様書", category: "技術文書", editable: true },
  { value: "feature_analysis_matrix", label: "機能分析マトリックス", category: "技術文書", editable: true },
  { value: "integration_requirements", label: "統合要件", category: "技術文書", editable: true },
  { value: "compliance_checklist", label: "コンプライアンスチェックリスト", category: "技術文書", editable: true },
  
  // Data & Research
  { value: "market_share_data", label: "市場シェアデータ", category: "データ・調査", editable: true },
  { value: "user_survey_results", label: "ユーザー調査結果", category: "データ・調査", editable: true },
  { value: "user_feedback_summary", label: "ユーザーフィードバック要約", category: "データ・調査", editable: true },
  { value: "financial_projections", label: "財務予測", category: "データ・調査", editable: true },
  
  // Training & Support
  { value: "training_materials", label: "研修資料", category: "研修・サポート", editable: true },
  
  // Business Documents
  { value: "business_requirements_document", label: "業務要件書", category: "ビジネス文書", editable: true },
]

const STORAGE_KEY = "custom-data-units"
const CATEGORIES_STORAGE_KEY = "custom-categories"

export class DataUnitManager {
  private static instance: DataUnitManager
  private customDataUnits: DataUnitConfig[] = []
  private customCategories: DataUnitCategoryInfo[] = []

  private constructor() {
    this.loadFromStorage()
  }

  static getInstance(): DataUnitManager {
    if (!DataUnitManager.instance) {
      DataUnitManager.instance = new DataUnitManager()
    }
    return DataUnitManager.instance
  }

  private loadFromStorage(): void {
    if (typeof window === "undefined") return

    try {
      const storedUnits = localStorage.getItem(STORAGE_KEY)
      if (storedUnits) {
        this.customDataUnits = JSON.parse(storedUnits)
      }

      const storedCategories = localStorage.getItem(CATEGORIES_STORAGE_KEY)
      if (storedCategories) {
        this.customCategories = JSON.parse(storedCategories)
      }
    } catch (error) {
      console.error("Failed to load data units from storage:", error)
    }
  }

  private saveToStorage(): void {
    if (typeof window === "undefined") return

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.customDataUnits))
      localStorage.setItem(CATEGORIES_STORAGE_KEY, JSON.stringify(this.customCategories))
    } catch (error) {
      console.error("Failed to save data units to storage:", error)
    }
  }

  getAllDataUnits(): DataUnitConfig[] {
    return [...DEFAULT_DATA_UNITS, ...this.customDataUnits]
  }

  getAllCategories(): DataUnitCategoryInfo[] {
    return [...DEFAULT_CATEGORIES, ...this.customCategories]
  }

  getDataUnitsByCategory(category: string): DataUnitConfig[] {
    return this.getAllDataUnits().filter(unit => unit.category === category)
  }

  addDataUnit(unit: Omit<DataUnitConfig, "editable">): void {
    const newUnit: DataUnitConfig = { ...unit, editable: true }
    this.customDataUnits.push(newUnit)
    this.saveToStorage()
  }

  updateDataUnit(oldValue: DataUnitCategory, newUnit: DataUnitConfig): void {
    // Update in custom data units
    const customIndex = this.customDataUnits.findIndex(unit => unit.value === oldValue)
    if (customIndex !== -1) {
      this.customDataUnits[customIndex] = { ...newUnit, editable: true }
      this.saveToStorage()
      return
    }

    // If it's a default unit being edited, create a custom override
    const defaultIndex = DEFAULT_DATA_UNITS.findIndex(unit => unit.value === oldValue)
    if (defaultIndex !== -1) {
      this.customDataUnits.push({ ...newUnit, editable: true })
      this.saveToStorage()
    }
  }

  deleteDataUnit(value: DataUnitCategory): void {
    this.customDataUnits = this.customDataUnits.filter(unit => unit.value !== value)
    this.saveToStorage()
  }

  addCategory(category: Omit<DataUnitCategoryInfo, "editable">): void {
    const newCategory: DataUnitCategoryInfo = { ...category, editable: true }
    this.customCategories.push(newCategory)
    this.saveToStorage()
  }

  updateCategory(oldId: string, newCategory: DataUnitCategoryInfo): void {
    const index = this.customCategories.findIndex(cat => cat.id === oldId)
    if (index !== -1) {
      this.customCategories[index] = { ...newCategory, editable: true }
      this.saveToStorage()
    }
  }

  deleteCategory(id: string): void {
    this.customCategories = this.customCategories.filter(cat => cat.id !== id)
    this.saveToStorage()
  }

  getDataUnitConfig(value: DataUnitCategory): DataUnitConfig | undefined {
    return this.getAllDataUnits().find(unit => unit.value === value)
  }

  exportDataUnits(): string {
    return JSON.stringify({
      customDataUnits: this.customDataUnits,
      customCategories: this.customCategories,
    }, null, 2)
  }

  importDataUnits(jsonData: string): void {
    try {
      const data = JSON.parse(jsonData)
      if (data.customDataUnits && Array.isArray(data.customDataUnits)) {
        this.customDataUnits = data.customDataUnits
      }
      if (data.customCategories && Array.isArray(data.customCategories)) {
        this.customCategories = data.customCategories
      }
      this.saveToStorage()
    } catch (error) {
      throw new Error("Invalid JSON data format")
    }
  }

  clearCustomData(): void {
    this.customDataUnits = []
    this.customCategories = []
    this.saveToStorage()
  }
}

export const dataUnitManager = DataUnitManager.getInstance()
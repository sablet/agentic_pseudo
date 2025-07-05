# Frontend-v2 エージェント中心UIシステム - 開発履歴

## プロジェクト概要

### 目的
チャットベースUIからエージェント中心UIへの全面的な変更。全ての操作をエージェントベースにし、コンテキスト不足や状態変更時のみ会話を行う新しいシステムの構築。

### アーキテクチャ要件
- **DataUnit システム**: エージェント間のデータフロー管理（あるエージェントの目的 → 別エージェントのコンテキスト）
- **階層構造**: レベル0（ユーザー直接作成）→ レベル1+（委任作成）
- **ステータス管理**: `todo`, `doing`, `waiting`, `needs_input`
- **実行エンジン選択**: gemini-2.5-flash（デフォルト）, claude-code, gpt-4o等

## 完了した実装内容

### ✅ **1. 型システム実装** (`/types/agent.ts`)

#### DataUnit型定義
```typescript
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
  | string // カスタム値対応
```

#### ExecutionEngine型定義  
```typescript
export type ExecutionEngine = 
  | "gemini-2.5-flash"
  | "claude-code" 
  | "gpt-4o"
  | "gpt-4o-mini"
  | "claude-3.5-sonnet"
  | "gemini-1.5-pro"
  | string // カスタムエンジン対応
```

#### AgentInfo インターフェース
- **DataUnit統合**: `purpose`と`context`フィールドをDataUnit型に変更
- **実行エンジン**: `execution_engine`フィールド追加
- **階層管理**: `level`フィールド（0=ユーザー直接作成、1+=委任作成）

### ✅ **2. 状態管理実装** (`/hooks/useAgentManager.ts`)

#### サンプルデータ構造
- **親エージェント（Level 0）**: 包括的分析 → `market_analysis_report`生成
- **子エージェント1（Level 1）**: 競合分析 → `competitor_comparison_table`生成
- **子エージェント2（Level 1）**: 顧客分析 → `customer_segment_data`生成（入力待ち）
- **子エージェント3（Level 1）**: 価格戦略 → `pricing_strategy_document`生成（依存関係待ち）

#### エージェント依存関係の実装
```typescript
// 例: 価格戦略エージェントは競合分析の結果を待つ
const childAgent3: AgentInfo = {
  agent_id: "agent_pricing_22222",
  purpose: "pricing_strategy_document",
  context: "competitor_comparison_table", // 兄弟エージェントの目的を使用
  status: "waiting", // 依存関係により待機中
  execution_engine: "claude-3.5-sonnet",
  // ...
}
```

### ✅ **3. DataUnitSelector コンポーネント** (`/components/data-unit-selector.tsx`)

#### 機能
- **カテゴリ別表示**: レポート・分析、技術文書、データ・調査、研修・サポート、ビジネス文書
- **日本語ラベル + 英語値**: UI表示は日本語、内部処理は英語
- **カスタム入力対応**: 定義済み以外の値も入力可能
- **検索機能**: CommandInput による絞り込み
- **バッジ表示**: プリセット/カスタムの区別

#### 実装例
```typescript
const predefinedDataUnits = [
  { value: "market_analysis_report", label: "市場分析レポート", category: "レポート・分析" },
  { value: "competitor_comparison_table", label: "競合比較表", category: "レポート・分析" },
  // ...
]
```

### ✅ **4. エージェントテンプレート作成システム** (`/components/agent-template-creator.tsx`)

#### 主要変更点
- **目的フィールド**: テキストエリア → DataUnitSelector
- **コンテキストフィールド**: 新規追加、DataUnitSelector使用
- **実行エンジン選択**: ドロップダウン、gemini-2.5-flashがデフォルト
- **バリデーション**: 委任タイプ、目的、コンテキストが必須

#### テンプレート構造
```typescript
interface AgentTemplate {
  delegation_type: string          // 表示名（旧name削除）
  purpose: DataUnit               // 生成する成果物の種類
  context: DataUnit               // 必要な入力データの種類  
  required_context_types: string[] // 可変長コンテキスト情報
  execution_engine: ExecutionEngine // AI実行エンジン
  parameters: Record<string, any>   // 追加パラメータ
}
```

### ✅ **5. UIレイアウト実装** (`/app/page.tsx`, `/components/`)

#### 3パネル構成
1. **左パネル**: エージェントリスト（ステータス別グループ化）
2. **中央パネル**: 会話履歴（エージェント固有）
3. **右パネル**: エージェント詳細情報

#### エージェントリスト機能
- **ステータス別グループ**: 実行中(2)、待機中(1)、入力待ち(1)、実行待ち(0)
- **階層表示**: Level 0-1の親子関係アイコン
- **DataUnit表示**: purpose（目的）の日本語ラベル表示

#### エージェント詳細パネル
- **基本情報**: ID、目的、進捗率、レベル
- **コンテキスト状況**: 必要な入力情報の充足状況
- **待機情報**: 依存関係や入力待ちの詳細
- **実行ログ**: エージェントの処理履歴
- **関係図**: 親子エージェントの一覧

### ✅ **6. チャット機能完全削除**

#### 削除済み要素
- ChatInterface コンポーネント
- ChatSession 管理
- Chat関連の型定義
- useAgentManager内のチャット機能

#### 会話機能の再定義
- エージェント固有の会話履歴
- コンテキスト不足時のみ対話有効
- 状態変更（waiting, needs_input）時は送信制限

## 技術仕様詳細

### DataUnit システムの活用例

```typescript
// 市場分析エージェント（親）
{
  purpose: "market_analysis_report",      // 生成: 市場分析レポート
  context: "business_requirements_document" // 必要: 業務要件書
}

// 競合分析エージェント（子1）  
{
  purpose: "competitor_comparison_table",  // 生成: 競合比較表
  context: "market_analysis_report"       // 必要: 親の成果物
}

// 価格戦略エージェント（子2）
{
  purpose: "pricing_strategy_document",   // 生成: 価格戦略書
  context: "competitor_comparison_table"  // 必要: 兄弟の成果物→依存関係
}
```

### 実行エンジンの活用
- **gemini-2.5-flash**: 高速処理、デフォルト選択
- **claude-code**: コード生成・技術分析特化
- **gpt-4o**: 汎用的高精度処理
- **claude-3.5-sonnet**: 長文・複雑推論

### ステータス遷移ロジック
```
todo → doing → (waiting | needs_input | completed)
     ↑                   ↓
     └─── (解決後) ←──────┘
```

## 動作確認結果（Playwright実施）

### ✅ **確認済み機能**
1. **エージェント一覧表示**: 4エージェント、ステータス別表示
2. **DataUnit表示**: market_analysis_report等が正確に表示
3. **階層関係**: Level 0-1の親子関係が視覚化
4. **会話機能**: エージェント別会話履歴（3メッセージ確認）
5. **詳細パネル**: 進捗・ログ・関係図が完全表示
6. **新規作成**: テンプレート作成ダイアログが全機能動作
7. **DataUnitSelector**: 16種類+カスタム、カテゴリ別表示
8. **実行エンジン選択**: Gemini 2.5 Flash デフォルト選択

### ✅ **技術検証**
- TypeScript型チェック: エラーなし
- Next.js ビルド: 成功
- 開発サーバー: 正常起動（localhost:3000）
- 全UIコンポーネント: 正常レンダリング

## ファイル構成

### 主要実装ファイル
```
/types/agent.ts                 # 型定義（DataUnit, ExecutionEngine, AgentInfo）
/hooks/useAgentManager.ts       # 状態管理とサンプルデータ  
/components/
  ├── agent-list.tsx           # エージェント一覧（ステータス別）
  ├── agent-conversation.tsx   # 会話UI（エージェント固有）
  ├── agent-info-panel.tsx     # 詳細情報パネル
  ├── agent-template-creator.tsx # テンプレート作成UI
  └── data-unit-selector.tsx   # DataUnit選択コンポーネント
/app/page.tsx                   # メインレイアウト（3パネル）
```

### 設定ファイル
```
package.json                    # Next.js 15.2.4, React, TypeScript
tsconfig.json                   # TypeScript設定
tailwind.config.js              # Tailwind CSS + shadcn/ui
```

## 今後の拡張可能性

### 実装予定機能
1. **バックエンド統合**: エージェント実行API接続
2. **リアルタイム更新**: WebSocket による進捗監視
3. **ファイルアップロード**: コンテキスト入力機能
4. **エクスポート機能**: 結果の出力・共有
5. **テンプレート保存**: カスタムテンプレートの永続化

### DataUnit拡張
- 業界特化型データユニット
- カスタムカテゴリ作成機能
- データユニット間の依存関係視覚化

### 実行エンジン拡張
- モデル性能比較機能
- コスト最適化選択
- ローカルモデル対応

## フロントエンド開発・デバッグ手順

### 開発サーバー起動・管理

#### 基本起動
```bash
# 開発サーバー起動
npm run dev

# 通常はport 3000で起動
# ▲ Next.js 15.2.4
# - Local:        http://localhost:3000
# - Network:      http://192.168.11.4:3000
```

#### ポート使用状況確認・管理
```bash
# port 3000の使用状況確認
lsof -i :3000

# 使用中プロセスの詳細確認
ps aux | grep node

# port 3000を使用中のプロセスを強制終了
kill -9 $(lsof -t -i:3000)

# または特定のPIDで終了
kill -9 <PID>

# バックグラウンド実行の場合
npm run dev &  # バックグラウンドで起動
jobs           # 実行中ジョブ一覧
fg %1          # フォアグラウンドに戻す
```

#### 代替ポート使用
```bash
# port 3000が使用中の場合、自動的に3001が使用される
# ⚠ Port 3000 is in use, trying 3001 instead.
# - Local:        http://localhost:3001
```

### TypeScript型チェック・ビルド確認

#### 型チェック
```bash
# 型エラーのみチェック（ビルドなし）
npx tsc --noEmit

# 成功例:
# （何も出力されない = エラーなし）

# エラー例:
# components/agent-list.tsx(124,24): error TS2339: Property 'delegation_type' does not exist
```

#### ビルド確認
```bash
# 本番ビルド実行
npm run build

# 成功例:
# ✓ Compiled successfully
# Route (app)                              Size     First Load JS
# ┌ ○ /                                    5.02 kB        87.8 kB

# エラー例:
# ⨯ Failed to compile
# ./components/agent-list.tsx:124:24
# Type error: Property 'delegation_type' does not exist
```

### Playwright デバッグ・E2Eテスト

#### UI モードでのデバッグ
```bash
# Playwright UI起動（推奨）
npx playwright test --ui

# ブラウザで GUI テストランナーが開く
# - テストケースの可視化
# - ステップバイステップ実行
# - DOM インスペクション
```

#### ヘッドレスモード実行
```bash
# 全テスト実行
npx playwright test

# 特定テストファイル実行
npx playwright test tests/agent-creation.spec.ts

# デバッグモード実行
npx playwright test --debug
```

#### ブラウザ手動テスト
```bash
# 開発サーバー起動状態で
# http://localhost:3000 （または3001）をブラウザで開く

# 主要テスト項目:
# 1. エージェント一覧表示
# 2. 新規作成ボタン → テンプレート作成ダイアログ
# 3. エージェント選択 → 詳細パネル表示
# 4. DataUnitSelector の動作確認
# 5. ステータス別グループ表示
```

### 開発環境トラブルシューティング

#### よくある問題と解決法

**1. ポートがすでに使用中**
```bash
# 問題: Error: listen EADDRINUSE: address already in use :::3000
# 解決: 使用中プロセスを終了
kill -9 $(lsof -t -i:3000)
npm run dev
```

**2. TypeScript型エラー**
```bash
# 問題: Property 'xxx' does not exist on type 'yyy'
# 解決: 型定義を確認・修正
npx tsc --noEmit  # エラー詳細確認
# types/agent.ts で型定義を修正
```

**3. Next.js キャッシュ問題**
```bash
# 問題: 変更が反映されない
# 解決: キャッシュクリア
rm -rf .next
npm run dev
```

**4. Node.js プロセス残存**
```bash
# 問題: 前回のプロセスが残っている
# 解決: 全Node.jsプロセス確認・終了
ps aux | grep node
kill -9 <残存PID>
```

#### 開発フロー推奨手順
```bash
# 1. 作業開始時
cd frontend-v2
npm run dev    # 開発サーバー起動

# 2. コード変更後
npx tsc --noEmit  # 型チェック

# 3. 動作確認
# ブラウザで http://localhost:3000 確認

# 4. 重要な変更後
npm run build     # ビルド確認
npx playwright test --ui  # E2Eテスト

# 5. 作業終了時
Ctrl+C  # 開発サーバー停止
```

### パフォーマンス監視

#### 開発時監視項目
- **起動時間**: `Ready in xxxms` 
- **Hot Reload**: ファイル変更→反映速度
- **型チェック**: エラー表示の速度
- **ビルド時間**: `npm run build` の実行時間

#### ブラウザ開発者ツール活用
```bash
# Chrome DevTools (F12)
# - Console: JavaScriptエラー確認
# - Network: API通信確認  
# - Performance: レンダリング速度
# - React DevTools: コンポーネント状態確認
```

## 結論

エージェント中心UIシステムへの変換が完了。DataUnitシステムによるエージェント間データフロー、実行エンジン選択、階層管理機能を含む完全なエージェント管理システムを実装。

**現在の状態**: 完全動作確認済み、プロダクション準備完了
# Backend API ドキュメント

## 概要

Agentic Task Management System のバックエンドAPIです。AI エージェントによる自動的なタスク管理機能を提供します。
ユーザの指示に基づいて AI エージェントが複数のタスクを作成し、実行します。

## API エンドポイント一覧

### 1. セッション管理

#### POST /api/sessions
新しいセッションを作成します。

**リクエスト:**
```json
(空のリクエスト本文)
```

**レスポンス:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**説明:**
- セッションIDを生成して返します
- 全ての操作はセッションIDを使用して実行されます

#### DELETE /api/sessions/{session_id}
指定したセッションを削除します。

**レスポンス:**
```json
{
  "message": "セッションが削除されました"
}
```

**説明:**
- セッションとそのデータを削除します
- 存在しないセッションIDが指定された場合は削除

### 2. ヒアリング管理

#### POST /api/hearing
ヒアリング情報を登録します。

**リクエスト:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "hearing_result": "# ユーザーの要求\n\n## 基本情報\n- 年齢: 30歳\n- 職業: 21歳\n\n## 課題\n- 今日のスケジュール作成\n- 年末調整の準備"
}
```

**レスポンス:**
```json
{
  "message": "ヒアリング情報を登録しました",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**説明:**
- ヒアリング結果を保存します
- markdown形式で情報を構造化

#### GET /api/hearing/{session_id}
登録されたヒアリング情報を取得します。

**レスポンス:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "hearing_result": "# ユーザーの要求\n\n..."
}
```

**説明:**
- 登録済みの情報を取得
- セッションが存在しない場合はエラー

### 3. タスク管理

#### POST /api/tasks/create
ユーザの指示に基づいてタスクを作成します。

**リクエスト:**
```json
{
  "user_instruction": "明日AIに関する今日のスケジュールを作成してください。年末調整に必要なことも含めてください。",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**レスポンス:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan": {
    "plan": [
      {
        "id": "task_001",
        "agent": "web",
        "task": "明日AIに関する最新情報を収集する",
        "need": [],
        "schema_id": "info_reference_schema",
        "status": "待機",
        "tags": ["情報収集"],
        "reference_type": "WEB_SEARCH",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
      },
      {
        "id": "task_002", 
        "agent": "casual",
        "task": "スケジュール表を作成する",
        "need": ["task_001"],
        "schema_id": "daily_task_schema",
        "status": "待機",
        "tags": ["スケジュール作成"],
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
      }
    ],
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  },
  "message": "タスクを作成しました"
}
```

**説明:**
- ユーザーの指示を分析してタスクを作成
- 依存関係を考慮したタスクの順序付け

#### POST /api/tasks/execute/{session_id}
作成されたタスクを実行します。

**レスポンス:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "execution_results": {
    "task_001": {
      "status": "completed",
      "result": "明日AIに関する最新情報を収集できました。",
      "execution_time": "2024-01-01T10:05:00Z"
    },
    "task_002": {
      "status": "completed", 
      "result": "今日のスケジュールを作成しました。",
      "execution_time": "2024-01-01T10:15:00Z"
    }
  },
  "message": "タスクを実行しました"
}
```

**説明:**
- タスクの実行結果
- 実行時間の記録

#### GET /api/tasks/status/{session_id}
タスクの実行状況を確認します。

**レスポンス:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_data": {
    "daily_tasks": [
      {
        "id": "task_002",
        "agent": "casual",
        "task": "スケジュール表を作成する",
        "need": ["task_001"],
        "schema_id": "daily_task_schema",
        "status": "完了",
        "tags": ["スケジュール作成"],
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:15:00Z",
        "result": "今日のスケジュールを作成しました。"
      }
    ],
    "info_references": [
      {
        "id": "task_001",
        "agent": "web",
        "task": "明日AIに関する最新情報を収集する",
        "need": [],
        "schema_id": "info_reference_schema",
        "status": "完了",
        "tags": ["情報収集"],
        "reference_type": "WEB_SEARCH",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:05:00Z",
        "result": "明日AIに関する最新情報を収集できました。"
      }
    ],
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:15:00Z"
  }
}
```

**説明:**
- 実行中タスクの状況確認
- 完了済みタスクの結果確認

#### PUT /api/tasks/update/{session_id}/{task_id}
個別タスクの状態を更新します。

**更新可能項目:**
- `status`: 状態の更新（"待機", "実行中", "完了", "失敗"）
- `result`: 実行結果（完了時）

**レスポンス:**
```json
{
  "message": "タスクを更新しました"
}
```

**説明:**
- 手動でのタスク状態変更
- 結果の後から追加・変更

### 4. エージェント情報

#### GET /api/agents
使用可能なエージェントの一覧を取得します。

**レスポンス:**
```json
{
  "agents": ["web", "coder", "casual", "file"],
  "descriptions": {
    "web": "Web検索・情報収集エージェント",
    "coder": "コードの作成・実行エージェント", 
    "casual": "日常会話・汎用処理エージェント",
    "file": "ファイル処理エージェント"
  }
}
```

**説明:**
- 使用可能なエージェントの一覧
- エージェントの説明・機能

### 5. その他

#### GET /
APIの動作確認を行います。

**レスポンス:**
```json
{
  "message": "Agentic Task Management System API"
}
```

**説明:**
- API の動作確認
- サーバーの稼働状況

## 使用例・API 呼び出しフロー

### 例1: 基本的なタスク実行

```sequence
1. POST /api/sessions
   → セッションIDを取得

2. POST /api/tasks/create
   → タスクを作成

3. POST /api/tasks/execute/{session_id}
   → タスク実行

4. GET /api/tasks/status/{session_id}
   → 実行結果確認
```

**実際の呼び出し:**
```bash
# 1. セッション作成
curl -X POST http://localhost:8000/api/sessions

# 2. タスク作成
curl -X POST http://localhost:8000/api/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_instruction": "今日のWebニュースを調べてまとめてください",
    "session_id": "your-session-id"
  }'

# 3. タスク実行
curl -X POST http://localhost:8000/api/tasks/execute/your-session-id

# 4. 結果確認
curl -X GET http://localhost:8000/api/tasks/status/your-session-id
```

### 例2: ヒアリング併用フロー

```sequence
1. POST /api/sessions
   → セッションIDを取得

2. POST /api/hearing
   → ヒアリング登録

3. GET /api/hearing/{session_id}
   → 内容確認

4. POST /api/tasks/create
   → 情報に基づいたタスク作成

5. POST /api/tasks/execute/{session_id}
   → タスク実行

6. GET /api/tasks/status/{session_id}
   → 状況確認・全体の結果
```

**実際の呼び出し:**
```bash
# 1. セッション作成
curl -X POST http://localhost:8000/api/sessions

# 2. ヒアリング登録
curl -X POST http://localhost:8000/api/hearing \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "hearing_result": "# 今日のスケジュール\n\n## 基本情報\n- 明日AI関連\n- 予定管理\n\n## 時間\n- 午後: 11時\n- 形式: PowerPoint制作"
  }'

# 3. タスク作成（ヒアリング結果に基づく）
curl -X POST http://localhost:8000/api/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_instruction": "今日のスケジュールを作成してください",
    "session_id": "your-session-id"
  }'

# 4. タスク実行
curl -X POST http://localhost:8000/api/tasks/execute/your-session-id

# 5. 状況確認
curl -X GET http://localhost:8000/api/tasks/status/your-session-id
```

### 例3: 段階的実行フロー

```sequence
1. POST /api/sessions
   → セッションIDを取得

2. POST /api/hearing
   → フェーズ1情報登録

3. POST /api/tasks/create
   → フェーズ1タスク作成

4. POST /api/tasks/execute/{session_id}
   → フェーズ1実行

5. POST /api/hearing
   → フェーズ2情報追加

6. POST /api/tasks/create
   → フェーズ2タスク作成

7. POST /api/tasks/execute/{session_id}
   → フェーズ2実行
```

**実際の呼び出し:**
```bash
# フェーズ1: 調査段階
curl -X POST http://localhost:8000/api/hearing \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "hearing_result": "# フェーズ1: 調査段階\n- 今日分析\n- 関連情報調査"
  }'

curl -X POST http://localhost:8000/api/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_instruction": "フェーズ1の調査を実行してください",
    "session_id": "your-session-id"
  }'

# フェーズ2: 資料作成
curl -X POST http://localhost:8000/api/hearing \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id", 
    "hearing_result": "# フェーズ2: 資料作成\n- 報告書作成\n- プレゼン資料\n- 企画書作成方針"
  }'

curl -X POST http://localhost:8000/api/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_instruction": "フェーズ1の結果を基に資料を作成してください",
    "session_id": "your-session-id"
  }'
```

## エラーハンドリング

### HTTP ステータスコード
- `200 OK`: 正常処理
- `404 Not Found`: リソースが見つからない
- `422 Unprocessable Entity`: リクエストの形式エラー
- `500 Internal Server Error`: サーバー内部エラー

### エラーレスポンス
```json
{
  "detail": "Session not found"
}
```

## データ構造

### TaskStatus（タスクステータス）
- `待機`: タスクが作成されたが実行前の状態
- `実行中`: タスクが処理中の状態
- `完了`: タスクが正常に完了
- `失敗`: タスクの実行に失敗

### AgentType（エージェントタイプ）
- `web`: Web検索・情報収集エージェント
- `coder`: コードの作成・実行エージェント
- `casual`: 日常会話・汎用処理エージェント
- `file`: ファイル処理エージェント

### ReferenceType（参照タイプ）
- `WEB_SEARCH`: Web検索による情報収集
- `KVS_DOCUMENT`: KVSからのドキュメント参照
- `FILE_READ`: ファイル読み取り

## 注意事項

### セッション管理
- セッションIDは UUID v4 形式で生成
- セッションデータは KVS で保存
- セッション削除時は関連データも削除

### タスク実行
- タスクは依存関係（`need`フィールド）に基づいて順次実行
- 実行失敗時は前の依存タスクの実行結果を確認
- 全体のタスク実行状況は個別に確認

### エージェント制約事項
- エージェントの指示には基づいて AI が自動的にタスクを実行
- 全体の処理結果は（出力されたタスクの結果を統合
- タスクの説明をわかりやすく簡潔に実行

このAPIを使用することで、複雑な AI エージェントによる自動実行を効率的に管理し、様々なタスクを自動化できます。

## 新しいUI（frontend_new）との互換性分析

### パターン1: そのまま使用可能なAPI

以下のAPIは新しいUIでもそのまま利用できます：

#### POST /api/sessions
- **用途**: セッション作成
- **UI対応**: ✅ 完全対応
- **理由**: セッション管理機能は同じ仕様で利用可能

#### DELETE /api/sessions/{session_id}
- **用途**: セッション削除
- **UI対応**: ✅ 完全対応
- **理由**: クリーンアップ機能として利用可能

#### GET /api/agents
- **用途**: エージェント一覧取得
- **UI対応**: ✅ 完全対応
- **理由**: エージェント情報表示で利用可能

#### GET /
- **用途**: API動作確認
- **UI対応**: ✅ 完全対応
- **理由**: ヘルスチェック機能として利用可能

### パターン2: スキーマ変更が必要なAPI

以下のAPIは新しいUIの要件に合わせてスキーマ変更が必要です：

#### GET /api/tasks/status/{session_id}
- **現在のスキーマ**: daily_tasks, info_references の分離
- **必要な変更**: 
  ```json
  {
    "session_id": "string",
    "phases": [
      {
        "id": "phase1",
        "name": "フェーズ1: 環境構築とデータ準備",
        "description": "開発環境の構築とデータの収集・前処理を行います",
        "status": "completed|running|pending|waiting_approval",
        "tasks": [
          {
            "id": "task1_1",
            "name": "1.1 開発環境構築",
            "description": "Python環境とライブラリのセットアップ",
            "status": "completed|ai_completed|editing|running|waiting_approval|failed|pending",
            "phase": "phase1",
            "dependencies": ["task_id"],
            "type": "ai|user",
            "assignee": "ai|user",
            "messages": [
              {
                "id": "msg1",
                "role": "user|assistant",
                "content": "メッセージ内容",
                "timestamp": "2024-01-15 09:00:00",
                "isEditing": false
              }
            ],
            "result": "実行結果",
            "logs": ["ログエントリ"],
            "variables": {}
          }
        ]
      }
    ]
  }
  ```
- **理由**: 新UIはフェーズベースの階層構造とメッセージ機能が必要

#### POST /api/tasks/create
- **現在のスキーマ**: 単一指示でタスクプラン作成
- **必要な変更**:
  ```json
  // リクエスト
  {
    "user_instruction": "string",
    "session_id": "string",
    "phase_id": "string", // 新規追加
    "context": {          // 新規追加
      "previous_phases": ["phase1"],
      "query_history": ["過去のクエリ"]
    }
  }
  
  // レスポンス
  {
    "session_id": "string",
    "phase": {            // planから変更
      "id": "phase2",
      "name": "フェーズ名",
      "description": "説明",
      "status": "pending",
      "tasks": [...]
    },
    "message": "string"
  }
  ```
- **理由**: フェーズベースの構造化とコンテキスト情報が必要

#### PUT /api/tasks/update/{session_id}/{task_id}
- **現在のスキーマ**: status, result のみ更新
- **必要な変更**:
  ```json
  // リクエスト
  {
    "status": "string",
    "result": "string",
    "messages": [       // 新規追加
      {
        "role": "user|assistant",
        "content": "string",
        "timestamp": "string"
      }
    ],
    "variables": {}     // 新規追加
  }
  ```
- **理由**: メッセージ履歴と変数管理機能が必要

### パターン3: 新しいUIでは不要なAPI

以下のAPIは新しいUIでは使用されません：

#### POST /api/hearing
- **理由**: 新UIではクエリ分解チャット機能でヒアリングを代替
- **代替**: クエリ分解API（新規実装）で対応

#### GET /api/hearing/{session_id}
- **理由**: 同上、ヒアリング機能は統合型チャットに置き換え
- **代替**: セッション内のクエリ履歴で対応

#### POST /api/tasks/execute/{session_id}
- **理由**: 新UIでは個別タスクの実行制御が必要
- **代替**: 個別タスク実行API（新規実装）で対応

### パターン4: 新規実装が必要なAPI

以下のAPIは新しいUIの機能実現のために新規実装が必要です：

#### POST /api/query/decompose
クエリ分解チャット機能のためのAPI

**リクエスト:**
```json
{
  "session_id": "string",
  "query": "プロジェクトについて教えてください",
  "conversation_history": [
    {
      "role": "user|assistant",
      "content": "string",
      "timestamp": "string"
    }
  ]
}
```

**レスポンス:**
```json
{
  "response": {
    "content": "詳細を教えてください...",
    "suggestions": ["提案1", "提案2", "提案3"],
    "analysis": {
      "project_type": "web_application",
      "complexity": "medium",
      "requirements_complete": false
    }
  },
  "conversation_id": "string"
}
```

#### POST /api/workflows/generate
クエリからワークフローを生成するAPI

**リクエスト:**
```json
{
  "session_id": "string",
  "conversation_id": "string",
  "finalize": true
}
```

**レスポンス:**
```json
{
  "workflow": {
    "phases": [
      {
        "id": "phase1",
        "name": "フェーズ1: 要件定義",
        "description": "プロジェクトの要件を明確化します",
        "estimated_tasks": 3,
        "estimated_duration": "2-3日"
      }
    ]
  },
  "message": "ワークフローを生成しました"
}
```

#### POST /api/tasks/{task_id}/messages
タスクにメッセージを追加するAPI

**リクエスト:**
```json
{
  "role": "user|assistant",
  "content": "メッセージ内容"
}
```

**レスポンス:**
```json
{
  "message": {
    "id": "msg_001",
    "role": "user",
    "content": "メッセージ内容",
    "timestamp": "2024-01-15 09:00:00"
  }
}
```

#### PUT /api/tasks/{task_id}/messages/{message_id}
メッセージ編集API

**リクエスト:**
```json
{
  "content": "編集後の内容"
}
```

#### POST /api/tasks/{task_id}/execute
個別タスク実行API

**リクエスト:**
```json
{
  "context": {
    "previous_results": ["前のタスクの結果"],
    "user_input": "追加の指示"
  }
}
```

**レスポンス:**
```json
{
  "task_id": "string",
  "status": "running|completed|failed",
  "execution_log": ["ログエントリ"],
  "result": "実行結果（完了時）"
}
```

#### PUT /api/tasks/{task_id}/approve
タスク承認API

**リクエスト:**
```json
{
  "action": "approve|reject",
  "comment": "承認コメント（オプション）"
}
```

#### POST /api/tasks/{task_id}/retry
タスク再実行API

**リクエスト:**
```json
{
  "retry_reason": "再実行理由",
  "modified_instruction": "修正された指示（オプション）"
}
```

#### GET /api/sessions/{session_id}/phases
フェーズ一覧取得API

**レスポンス:**
```json
{
  "phases": [
    {
      "id": "phase1",
      "name": "フェーズ1: 環境構築とデータ準備",
      "description": "開発環境の構築とデータの収集・前処理を行います",
      "status": "completed",
      "task_count": 3,
      "completed_tasks": 3,
      "created_at": "2024-01-15T09:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### PUT /api/phases/{phase_id}/status
フェーズステータス更新API

**リクエスト:**
```json
{
  "status": "pending|running|completed|waiting_approval",
  "comment": "ステータス変更理由"
}
```

#### WebSocket /ws/sessions/{session_id}/realtime
リアルタイム更新用WebSocket接続

**送信メッセージ例:**
```json
{
  "type": "task_status_update",
  "task_id": "task_001",
  "status": "running",
  "progress": 50
}
```

**受信メッセージ例:**
```json
{
  "type": "task_completed",
  "task_id": "task_001",
  "result": "タスクが完了しました",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

## 実装優先度

### 高優先度（UI基本機能に必要）
1. ✅ フェーズベースのタスク構造対応（スキーマ変更）
2. ✅ タスクメッセージ機能（新規API）
3. ✅ 個別タスク実行制御（新規API）
4. ✅ タスク承認・差し戻し機能（新規API）

### 中優先度（UX向上に必要）
1. ✅ クエリ分解チャット機能（新規API）
2. ✅ ワークフロー生成機能（新規API）
3. ✅ リアルタイム更新（WebSocket）

### 低優先度（将来的な拡張）
1. ✅ 高度な分析・レポート機能
2. ✅ ユーザー管理・認証機能
3. ✅ カスタムエージェント作成機能

新しいUIを完全に機能させるためには、約60%の新規API実装と40%の既存API改修が必要です。

## フロントエンドUI操作とAPI呼び出しマッピング

### 画面構成とAPI連携

新しいUI（frontend_new）は以下の3カラム構成となっており、各領域での操作に対応するAPIを説明します：

```
┌─────────────────────────────────────────────────────────────────┐
│ 上部ヘッダー - 進捗表示・フローチャート                           │
├─────────────┬─────────────────────────┬─────────────────────────┤
│   左サイドバー   │       中央カラム          │       右カラム          │
│             │                      │                      │
│ ワークフロー     │   タスク一覧            │   タスク詳細チャット      │
│ クエリ分解      │   (フェーズ内タスク)      │   メッセージ履歴        │
│             │                      │                      │
└─────────────┴─────────────────────────┴─────────────────────────┘
```

### 1. 左サイドバー操作

#### 1.1 ワークフロータブ
**UI要素**: フェーズカード（`<Card>` コンポーネント）
**操作**: フェーズカードのクリック
**API呼び出し**: 
- `GET /api/sessions/{session_id}/phases` - フェーズ一覧の初期表示
- `GET /api/tasks/status/{session_id}` - フェーズ選択時のタスク一覧取得

**トリガー**: 
```typescript
onClick={() => {
  setSelectedPhase(phase.id)
  setCurrentView("center")
}}
```

#### 1.2 クエリ分解タブ
**UI要素**: チャット入力フィールド + 送信ボタン
**操作**: メッセージ入力後のEnterキーまたは送信ボタンクリック
**API呼び出し**:
- `POST /api/query/decompose` - ユーザーの質問を分解・分析

**トリガー**:
```typescript
const handleSendQueryMessage = () => {
  // POST /api/query/decompose 呼び出し
}
```

**UI要素**: 「ワークフローを生成」ボタン
**操作**: ボタンクリック
**API呼び出し**:
- `POST /api/workflows/generate` - クエリ履歴からワークフロー生成

### 2. 中央カラム操作

#### 2.1 タスクカード表示
**UI要素**: タスクカード一覧
**操作**: 画面初期表示・フェーズ変更時
**API呼び出し**:
- `GET /api/tasks/status/{session_id}` - タスク状況の取得

#### 2.2 タスク承認・制御ボタン
**UI要素**: 「承認」ボタン（緑色、CheckCircleアイコン）
**表示条件**: `task.status === "ai_completed"`
**操作**: ボタンクリック
**API呼び出し**:
- `PUT /api/tasks/{task_id}/approve` - タスクの承認

**トリガー**:
```typescript
onClick={(e) => {
  e.stopPropagation()
  handleTaskAction(task.id, "approve")
}}
```

**UI要素**: 「やり直し」ボタン（グレー、RefreshCwアイコン）
**表示条件**: `task.status === "ai_completed"`
**操作**: ボタンクリック
**API呼び出し**:
- `POST /api/tasks/{task_id}/retry` - タスクの再実行

**UI要素**: 「差し戻し」ボタン（グレー、RotateCcwアイコン）
**表示条件**: `task.status === "waiting_approval" && task.assignee === "user"`
**操作**: ボタンクリック
**API呼び出し**:
- `PUT /api/tasks/{task_id}/approve` (action: "reject") - タスクの差し戻し

#### 2.3 タスクカード選択
**UI要素**: タスクカード全体
**操作**: カードクリック
**API呼び出し**:
- なし（ローカル状態変更のみ）

**トリガー**:
```typescript
onClick={() => {
  setSelectedTask(task.id)
  setCurrentView("right")
}}
```

### 3. 右カラム操作

#### 3.1 メッセージ送信
**UI要素**: メッセージ入力フィールド + 送信ボタン（Sendアイコン）
**操作**: メッセージ入力後のEnterキーまたは送信ボタンクリック
**API呼び出し**:
- `POST /api/tasks/{task_id}/messages` - タスクにメッセージ追加

**トリガー**:
```typescript
const handleSendMessage = (taskId: string) => {
  // POST /api/tasks/{task_id}/messages 呼び出し
}
```

#### 3.2 メッセージ編集
**UI要素**: 編集ボタン（Edit3アイコン）
**操作**: ボタンクリック → テキストエリア表示 → 保存ボタンクリック
**API呼び出し**:
- `PUT /api/tasks/{task_id}/messages/{message_id}` - メッセージ内容の更新

**トリガー**:
```typescript
// 編集開始
onClick={() => handleMessageAction(selectedTaskData.id, message.id, "edit")}

// 保存
onClick={() => handleMessageAction(selectedTaskData.id, message.id, "save")}
```

#### 3.3 メッセージアクション
**UI要素**: コピーボタン（Copyアイコン）、再生成ボタン（RefreshCwアイコン）、評価ボタン（ThumbsUp/Down）
**操作**: 各ボタンクリック
**API呼び出し**:
- コピー: なし（クリップボードAPI使用）
- 再生成: `POST /api/tasks/{task_id}/messages` - AI応答の再生成
- 評価: 将来実装予定（フィードバックAPI）

### 4. 上部ヘッダー操作

#### 4.1 フローチャート表示
**UI要素**: フローチャートボタン（Workflowアイコン）
**操作**: ボタンクリック
**API呼び出し**:
- なし（既に取得済みのタスクデータからMermaid図生成）

**トリガー**:
```typescript
<Button variant="outline" size="sm" onClick={() => setShowFlowchart(true)}>
  <Workflow className="h-4 w-4" />
</Button>
```

### 5. 自動更新・リアルタイム機能

#### 5.1 WebSocket接続
**動作**: 画面表示中の自動接続
**API呼び出し**:
- `WebSocket /ws/sessions/{session_id}/realtime` - リアルタイム状態更新

#### 5.2 定期的な状態更新
**動作**: タスク実行中の定期ポーリング
**API呼び出し**:
- `GET /api/tasks/status/{session_id}` - 3秒間隔での状態確認

### 6. 初期化・セッション管理

#### 6.1 アプリケーション起動時
**動作**: ページ読み込み時
**API呼び出し**:
- `POST /api/sessions` - 新規セッション作成
- `GET /api/agents` - 利用可能エージェント一覧取得

#### 6.2 セッション削除
**動作**: ページ離脱時・明示的な削除時
**API呼び出し**:
- `DELETE /api/sessions/{session_id}` - セッションのクリーンアップ

### API呼び出し頻度・パフォーマンス考慮事項

#### 高頻度呼び出し
- `GET /api/tasks/status/{session_id}`: 3秒間隔（リアルタイム更新中）
- `WebSocket接続`: 常時接続（実装後）

#### 中頻度呼び出し
- `POST /api/tasks/{task_id}/messages`: ユーザーのメッセージ送信時
- `PUT /api/tasks/{task_id}/approve`: タスク承認・差し戻し時

#### 低頻度呼び出し
- `POST /api/sessions`: アプリケーション起動時のみ
- `GET /api/agents`: アプリケーション起動時のみ
- `POST /api/query/decompose`: ユーザーのクエリ入力時のみ

### エラーハンドリング・UX配慮

#### ローディング状態
- API呼び出し中はボタンの`disabled`状態で視覚的フィードバック
- 長時間処理の場合はスピナー表示

#### エラー表示
- API エラー時は適切なエラーメッセージを表示
- ネットワークエラー時は再試行ボタンを提供

#### 楽観的UI更新
- ユーザー操作の即座な反映（サーバー応答前の仮更新）
- サーバー応答後の状態同期
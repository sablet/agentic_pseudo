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
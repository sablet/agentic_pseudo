# Backend API v2 - Frontend-v2 対応仕様

## 概要

Frontend-v2 コンポーネントの分析に基づいて、エージェント通信システムに必要なバックエンドAPIを整理し、データスキーマを定義します。

## API関連性ダイアグラム

### 1. APIエンドポイント関係図（フローチャート）

```mermaid
flowchart TD
    A[Client] --> B["GET /api/agents"]
    A --> C["GET /api/chat/sessions"]
    
    B --> D["POST /api/agents"]
    D --> E[Agent Created]
    E --> F["POST /api/notifications"]
    
    C --> G["GET /api/chat/sessions/{agent_id}/messages"]
    G --> H["POST /api/chat/sessions/{agent_id}/messages"]
    
    H --> I{Contains agent_proposal?}
    I -->|Yes| J["POST /api/agents/proposals/{id}/approve"]
    I -->|No| K[Normal Message]
    
    J --> D
    
    E --> L["POST /api/agents/{agent_id}/execute"]
    L --> M["PUT /api/agents/{agent_id}/status"]
    
    M --> N[WebSocket Notification]
    N --> O["WebSocket Connection"]
    
    style E fill:#e1f5fe
    style F fill:#f3e5f5
    style N fill:#e8f5e8
```

### 2. データフロー図（状態遷移）

```mermaid
stateDiagram-v2
    [*] --> AgentDiscovery
    AgentDiscovery --> AgentCreation : POST agents
    AgentCreation --> AgentPending : status pending
    
    AgentPending --> AgentExecuting : POST execute
    AgentExecuting --> AgentCompleted : PUT status
    AgentExecuting --> AgentFailed : PUT status
    
    AgentCompleted --> [*]
    AgentFailed --> AgentPending : Retry
    
    state ChatFlow {
        [*] --> GetSessions
        GetSessions --> GetMessages : GET messages
        GetMessages --> SendMessage : POST messages
        SendMessage --> ProposalCheck
        ProposalCheck --> AgentProposal : Has proposal
        ProposalCheck --> NormalMessage : No proposal
        AgentProposal --> ApproveProposal : POST approve
        ApproveProposal --> AgentCreation
    }
    
    state NotificationFlow {
        [*] --> CreateNotification
        CreateNotification --> SendNotification : POST notifications
        SendNotification --> WebSocketBroadcast : WebSocket
    }
```

### 3. システム相互作用図（シーケンス）

```mermaid
sequenceDiagram
    participant U as User/Frontend
    participant A as Agent API
    participant C as Chat API
    participant N as Notification API
    participant W as WebSocket
    
    U->>A: GET /api/agents
    A-->>U: Available agent templates
    
    U->>C: GET /api/chat/sessions
    C-->>U: Session list
    
    U->>C: POST /api/chat/sessions/main/messages
    Note over C: User sends message
    C-->>U: Message with agent_proposal
    
    U->>A: POST /api/agents/proposals/{id}/approve
    A->>A: Create new agent
    A-->>U: Agent created
    
    A->>N: POST /api/notifications
    N->>W: Broadcast agent_created
    W-->>U: Real-time update
    
    U->>A: POST /api/agents/{id}/execute
    A->>A: Start execution
    A->>W: Broadcast status update
    W-->>U: Real-time status
    
    loop Execution Progress
        A->>A: PUT /api/agents/{id}/status
        A->>W: Broadcast progress
        W-->>U: Status updates
    end
    
    A->>C: POST /api/chat/sessions/{id}/messages
    Note over C: Agent posts result
    C->>W: Broadcast new message
    W-->>U: New message notification
```

### 4. アーキテクチャ概要図（C4スタイル）

```mermaid
graph TB
    subgraph Frontend["Frontend Layer"]
        UI[React Components]
        WS[WebSocket Client]
    end
    
    subgraph Gateway["API Gateway"]
        AG[API Gateway/Router]
    end
    
    subgraph Backend["Backend Services"]
        subgraph AgentMgmt["Agent Management"]
            A1["GET agents"]
            A2["POST agents"]
            A3["GET agent by ID"]
            A4["PUT agent status"]
            A5["POST agent execute"]
        end
        
        subgraph ChatMgmt["Chat Management"]
            C1["GET sessions"]
            C2["GET messages"]
            C3["POST messages"]
        end
        
        subgraph Proposal["Proposal System"]
            P1["POST approve"]
        end
        
        subgraph Notify["Notification System"]
            N1["POST notifications"]
            N2["WebSocket Server"]
        end
    end
    
    subgraph Data["Data Layer"]
        DB[(Database)]
        CACHE[(Cache/Session Store)]
    end
    
    UI --> AG
    WS --> N2
    AG --> A1
    AG --> A2
    AG --> A3
    AG --> A4
    AG --> A5
    AG --> C1
    AG --> C2
    AG --> C3
    AG --> P1
    AG --> N1
    
    A2 --> P1
    A4 --> N2
    P1 --> A2
    N1 --> N2
    
    A1 --> DB
    A2 --> DB
    A3 --> DB
    A4 --> DB
    A5 --> DB
    C1 --> DB
    C2 --> DB
    C3 --> DB
    P1 --> DB
    N1 --> CACHE
    N2 --> CACHE
    
    style UI fill:#e3f2fd
    style WS fill:#e8f5e8
    style DB fill:#fff3e0
    style CACHE fill:#fce4ec
```

### 5. データ関係図（ER図スタイル）

```mermaid
erDiagram
    AGENT {
        string agent_id PK
        string parent_agent_id FK
        string purpose
        string context
        string delegation_type
        string status
        json delegation_params
        datetime created_at
        datetime updated_at
    }
    
    CHAT_SESSION {
        string agent_id PK
        string agent_name
        int message_count
        datetime last_message_at
    }
    
    CHAT_MESSAGE {
        string id PK
        string role
        string content
        datetime timestamp
        string agent_id FK
        json agent_proposal
    }
    
    AGENT_TEMPLATE {
        string id PK
        string name
        string delegation_type
        string description
        string default_context
        json parameters
    }
    
    NOTIFICATION {
        string id PK
        string content
        string target_session
        string type
        datetime timestamp
    }
    
    AGENT ||--o{ AGENT : "parent-child"
    CHAT_SESSION ||--o{ CHAT_MESSAGE : "contains"
    AGENT ||--|| CHAT_SESSION : "has"
    AGENT_TEMPLATE ||--o{ AGENT : "creates"
```

## 必要なAPIエンドポイント

### 1. エージェント管理

#### GET /api/agents
利用可能なエージェント一覧とテンプレートを取得

**レスポンス:**
```json
{
  "agents": [
    {
      "id": "information_gathering",
      "name": "情報収集エージェント",
      "description": "指定されたトピックについて情報を収集し、整理して報告します",
      "delegation_type": "information_gathering",
      "default_context": "以下のトピックについて詳細な情報を収集してください：",
      "parameters": {
        "search_depth": "detailed",
        "source_types": ["web", "academic", "news"],
        "max_results": 10
      }
    },
    {
      "id": "analysis",
      "name": "分析エージェント",
      "description": "データや情報を分析し、洞察を提供します",
      "delegation_type": "analysis",
      "default_context": "以下のデータを分析し、重要な洞察を抽出してください：",
      "parameters": {
        "analysis_type": "comprehensive",
        "include_charts": true,
        "confidence_threshold": 0.8
      }
    },
    {
      "id": "summarization",
      "name": "要約エージェント",
      "description": "長い文書や情報を簡潔に要約します",
      "delegation_type": "summarization",
      "default_context": "以下の内容を要約してください：",
      "parameters": {
        "summary_length": "medium",
        "include_key_points": true,
        "format": "bullet_points"
      }
    }
  ]
}
```

#### POST /api/agents
新しいエージェントを作成

**リクエスト:**
```json
{
  "purpose": "AI技術の調査と分析",
  "delegation_type": "information_gathering",
  "context": "最新のAI技術トレンドについて調査し、競合分析を行ってください",
  "parent_agent_id": null,
  "delegation_params": {
    "search_keywords": ["AI", "機械学習", "深層学習"],
    "analysis_depth": "detailed"
  }
}
```

**レスポンス:**
```json
{
  "agent": {
    "agent_id": "agent_1703123456_abc123def",
    "parent_agent_id": null,
    "purpose": "AI技術の調査と分析",
    "context": "最新のAI技術トレンドについて調査し、競合分析を行ってください",
    "delegation_type": "information_gathering",
    "status": "pending",
    "delegation_params": {
      "search_keywords": ["AI", "機械学習", "深層学習"],
      "analysis_depth": "detailed"
    },
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
}
```

#### GET /api/agents/{agent_id}
特定のエージェント情報を取得

**レスポンス:**
```json
{
  "agent": {
    "agent_id": "agent_1703123456_abc123def",
    "parent_agent_id": null,
    "purpose": "AI技術の調査と分析",
    "context": "最新のAI技術トレンドについて調査し、競合分析を行ってください",
    "delegation_type": "information_gathering",
    "status": "in_progress",
    "delegation_params": {
      "search_keywords": ["AI", "機械学習", "深層学習"],
      "analysis_depth": "detailed"
    },
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:15:00Z"
  }
}
```

#### PUT /api/agents/{agent_id}/status
エージェントのステータスを更新

**リクエスト:**
```json
{
  "status": "in_progress" | "completed" | "failed" | "delegated"
}
```

#### POST /api/agents/{agent_id}/execute
エージェントの実行を開始

**レスポンス:**
```json
{
  "agent_id": "agent_1703123456_abc123def",
  "status": "in_progress",
  "message": "エージェントの実行を開始しました"
}
```

### 2. チャット・メッセージ管理

#### GET /api/chat/sessions
チャットセッション一覧を取得

**レスポンス:**
```json
{
  "sessions": [
    {
      "agent_id": null,
      "agent_name": "メインチャット",
      "message_count": 5,
      "last_message_at": "2024-01-01T10:30:00Z"
    },
    {
      "agent_id": "agent_1703123456_abc123def",
      "agent_name": "AI技術の調査と分析",
      "message_count": 3,
      "last_message_at": "2024-01-01T10:25:00Z"
    }
  ]
}
```

#### GET /api/chat/sessions/{agent_id}/messages
特定のセッションのメッセージ履歴を取得

**レスポンス:**
```json
{
  "messages": [
    {
      "id": "msg_1703123456_def456ghi",
      "role": "system_notification",
      "content": "エージェント間情報受け渡しシステムへようこそ。新しいエージェントの生成や既存エージェントの管理を行えます。",
      "timestamp": "2024-01-01T10:00:00Z",
      "agent_id": null
    },
    {
      "id": "msg_1703123460_ghi789jkl",
      "role": "user",
      "content": "AI技術について調査してください",
      "timestamp": "2024-01-01T10:10:00Z",
      "agent_id": null
    },
    {
      "id": "msg_1703123465_jkl012mno",
      "role": "assistant",
      "content": "この作業は専門的なエージェントに委任することをお勧めします。以下のエージェントを生成しますか？",
      "timestamp": "2024-01-01T10:11:00Z",
      "agent_id": null,
      "agent_proposal": {
        "purpose": "AI技術について調査してくださいに関する情報収集と分析",
        "delegation_type": "information_gathering",
        "context": "ユーザーからの要求: \"AI技術について調査してください\"に基づいて、関連する情報を収集し、分析結果を提供する。",
        "delegation_params": {
          "search_keywords": ["AI技術", "について", "調査"],
          "analysis_depth": "detailed"
        }
      }
    }
  ]
}
```

#### POST /api/chat/sessions/{agent_id}/messages
メッセージを送信

**リクエスト:**
```json
{
  "role": "user",
  "content": "進捗はどうですか？",
  "agent_proposal": null
}
```

**レスポンス:**
```json
{
  "message": {
    "id": "msg_1703123470_mno345pqr",
    "role": "user",
    "content": "進捗はどうですか？",
    "timestamp": "2024-01-01T10:30:00Z",
    "agent_id": "agent_1703123456_abc123def"
  }
}
```

### 3. エージェント提案・承認

#### POST /api/agents/proposals/{proposal_id}/approve
エージェント提案を承認

**リクエスト:**
```json
{
  "agent_proposal": {
    "purpose": "AI技術について調査してくださいに関する情報収集と分析",
    "delegation_type": "information_gathering",
    "context": "ユーザーからの要求: \"AI技術について調査してください\"に基づいて、関連する情報を収集し、分析結果を提供する。",
    "delegation_params": {
      "search_keywords": ["AI技術", "について", "調査"],
      "analysis_depth": "detailed"
    }
  }
}
```

**レスポンス:**
```json
{
  "agent": {
    "agent_id": "agent_1703123480_pqr456stu",
    "parent_agent_id": null,
    "purpose": "AI技術について調査してくださいに関する情報収集と分析",
    "context": "ユーザーからの要求: \"AI技術について調査してください\"に基づいて、関連する情報を収集し、分析結果を提供する。",
    "delegation_type": "information_gathering",
    "status": "pending",
    "delegation_params": {
      "search_keywords": ["AI技術", "について", "調査"],
      "analysis_depth": "detailed"
    },
    "created_at": "2024-01-01T10:35:00Z",
    "updated_at": "2024-01-01T10:35:00Z"
  }
}
```

### 4. システム通知

#### POST /api/notifications
システム通知を送信

**リクエスト:**
```json
{
  "content": "新しいエージェント「AI技術の調査と分析」が生成されました。",
  "target_session": null,
  "type": "agent_created"
}
```

**レスポンス:**
```json
{
  "notification": {
    "id": "notif_1703123490_stu789vwx",
    "content": "新しいエージェント「AI技術の調査と分析」が生成されました。",
    "timestamp": "2024-01-01T10:40:00Z",
    "type": "agent_created"
  }
}
```

## データスキーマ

### AgentInfo
```typescript
interface AgentInfo {
  agent_id: string;
  parent_agent_id: string | null;
  purpose: string;
  context: string;
  delegation_type: string;
  status: "pending" | "in_progress" | "completed" | "failed" | "delegated";
  delegation_params?: Record<string, any>;
  created_at: Date;
  updated_at: Date;
}
```

### ChatMessage
```typescript
interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system" | "system_notification";
  content: string;
  timestamp: Date;
  agent_id?: string; // どのエージェントのチャットに属するか
  agent_proposal?: {
    purpose: string;
    delegation_type: string;
    context: string;
    delegation_params?: Record<string, any>;
  };
}
```

### ChatSession
```typescript
interface ChatSession {
  agent_id: string | null; // nullはメインセッション
  agent_name: string;
  message_count: number;
  last_message_at: Date;
}
```

### AgentTemplate
```typescript
interface AgentTemplate {
  id: string;
  name: string;
  delegation_type: string;
  description: string;
  default_context: string;
  parameters: Record<string, any>;
}
```

### AgentNode (関係性ビュー用)
```typescript
interface AgentNode {
  id: string;
  label: string;
  status: AgentInfo["status"];
  x?: number;
  y?: number;
}
```

### AgentEdge (関係性ビュー用)
```typescript
interface AgentEdge {
  from: string;
  to: string;
  label?: string;
}
```

## WebSocket リアルタイム通信

### 接続エンドポイント
```
ws://localhost:8000/ws/agents/realtime
```

### 送信メッセージ形式
```json
{
  "type": "subscribe",
  "session_id": "session_123"
}
```

### 受信メッセージ形式
```json
{
  "type": "agent_status_update",
  "agent_id": "agent_1703123456_abc123def",
  "status": "completed",
  "timestamp": "2024-01-01T10:45:00Z"
}
```

```json
{
  "type": "new_message",
  "session_id": "agent_1703123456_abc123def",
  "message": {
    "id": "msg_1703123500_vwx012yz",
    "role": "assistant",
    "content": "調査が完了しました。AIに関する最新情報をまとめました。",
    "timestamp": "2024-01-01T10:50:00Z",
    "agent_id": "agent_1703123456_abc123def"
  }
}
```

## 認証・セキュリティ

### セッション管理
- セッション作成時にUUIDを生成
- WebSocketはセッションIDで認証
- APIキーによる認証（将来実装）

### データ検証
- 全APIエンドポイントでリクエストボディのバリデーション
- エージェント作成時のパラメータ検証
- メッセージ内容のサニタイズ

## エラーハンドリング

### HTTPステータスコード
- `200 OK`: 正常処理
- `201 Created`: リソース作成成功
- `400 Bad Request`: リクエストエラー
- `404 Not Found`: リソースが見つからない
- `422 Unprocessable Entity`: バリデーションエラー
- `500 Internal Server Error`: サーバーエラー

### エラーレスポンス形式
```json
{
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "指定されたエージェントが見つかりません",
    "details": {
      "agent_id": "agent_invalid_id"
    }
  }
}
```

## 実装優先順位

### 高優先度
1. **エージェント管理API** - 基本的なCRUD操作
2. **チャット・メッセージAPI** - メッセージ送受信
3. **エージェント提案・承認** - ワークフロー制御

### 中優先度
1. **WebSocketリアルタイム通信** - UX向上
2. **システム通知** - 状態変更の通知
3. **エラーハンドリング強化** - 安定性向上

### 低優先度
1. **認証・セキュリティ** - 将来の機能拡張
2. **ログ・監視** - 運用面の改善
3. **APIドキュメント自動生成** - 開発効率化

## 互換性考慮

### 既存APIとの関係
- 既存のタスク管理APIとは別系統として実装
- 必要に応じてデータ移行ツールを提供
- 段階的な移行を想定した設計

### フロントエンド要件
- TypeScript型定義の提供
- OpenAPI仕様書の自動生成
- モックサーバーの提供（開発時）

この仕様に基づいて、frontend-v2 コンポーネントが期待する全ての機能を実装可能です。
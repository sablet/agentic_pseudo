### タスク管理システム プロトタイプ設計案

#### 1\. システムの全体像（ハイレベルアーキテクチャ）

このシステムは、ユーザーからのタスク管理に関する指示をPlanner Agentが受け取り、それを具体的なタスク（日次・日中行動レベルのタスク、情報参照タスク）に分解し、KVSに保存された情報やスキーマを参照しながら実行する、という流れを基本とします。

```mermaid
graph TD
    User[ユーザー] -->|タスク指示| FrontEnd[ユーザーインターフェース]
    FrontEnd -->|タスク要求| PlannerAgent[Planner Agent]
    PlannerAgent -->|タスク計画/実行指示| SubAgents(Web, Coder, Casual, File Agentなど)
    PlannerAgent -->|タスクデータ保存/参照| KVS[KVS (Upstash)]
    PlannerAgent -->|ヒアリング結果保存/参照| KVS
    SubAgents -->|実行結果/情報| PlannerAgent
    KVS -->|スキーマ/タスクデータ| PlannerAgent
    KVS -->|ヒアリング結果| PlannerAgent
```

**主要コンポーネントの役割:**

  * **ユーザーインターフェース (FrontEnd)**: ユーザーがタスクを入力し、進捗を確認するための接点。将来的には、タスクの一覧表示やフィルタリング機能も提供。
  * **Planner Agent**:
      * ユーザーの複雑なタスク指示を、より小さなサブタスク（日次・日中行動レベルのタスク、情報参照タスク）に分解し、実行計画を生成します。
      * KVSからタスクのスキーマ定義や関連するヒアリング結果を参照し、計画に反映します。
      * 各サブタスクを適切なSub-Agent（Web, Coder, Casual, File Agentなど）に割り当て、実行を調整します。
      * タスクの実行結果を評価し、必要に応じて計画を動的に更新します。
      * タスクの状態や完了情報をKVSに保存します。
  * **Sub-Agents**:
      * **Web Agent**: 外部情報の検索、Webページの参照など。
      * **Coder Agent**: データ処理、スクリプト実行など。
      * **Casual Agent**: 自然言語処理、ユーザーとの対話など。
      * **File Agent**: ファイル操作、ドキュメント生成など。
      * （将来的には、タスク管理システムに特化したカスタムAgentも検討）
  * **KVS (Upstash)**:
      * **ヒアリング結果の保存**: `ユーザーセッションID`をキーとして、これまでのヒアリング内容をMarkdown形式で保存。
      * **タスクスキーマの保存**: `task_schemas:ユーザーセッションID`をキーとして、`daily_task_schema`と`info_reference_schema`を含むJSON形式で保存。
      * **タスクデータの保存**: `tasks:ユーザーセッションID`をキーとして、`daily_tasks`と`info_references`に分かれたJSON形式で、実際のタスクデータを保存。

#### 2\. データフローとコンポーネント間の連携

1.  **ユーザーからのタスク指示**: ユーザーが「〇〇のレポートを作成したい。その前に必要な情報収集をしておいてほしい」といった指示をFrontEndに入力。
2.  **Planner Agentによる計画生成**:
      * Planner Agentはユーザーの指示を受け取り、KVSから`task_schemas:ユーザーセッションID`をキーとしてタスクスキーマ定義を取得。
      * Planner Agentは、このスキーマとユーザーの指示、そして過去のヒアリング結果（`ユーザーセッションID`をキーとして取得）を考慮し、JSON形式の実行計画を生成。
      * この計画には、`daily_tasks`と`info_references`の両方のタイプのタスクが含まれる。
      * 例:
        ```json
        {
          "plan": [
            {
              "id": "info_001",
              "agent": "web",
              "task": "「〇〇レポートに必要な情報」を検索",
              "need": [],
              "schema_id": "info_reference_schema",
              "status": "未着手",
              "tags": ["情報収集"]
            },
            {
              "id": "task_001",
              "agent": "casual", // または特定のレポート作成Agent
              "task": "〇〇レポートのドラフト作成",
              "need": ["info_001"], // 情報収集が前提条件
              "schema_id": "daily_task_schema",
              "status": "未着手",
              "tags": ["レポート"]
            }
          ]
        }
        ```
3.  **タスクデータのKVS保存**: Planner Agentは生成した計画内の各タスクを、`tasks:ユーザーセッションID`のKVSエントリ内の適切なリスト（`daily_tasks`または`info_references`）に追加して保存。
4.  **Sub-Agentによるタスク実行**:
      * Planner Agentは計画に従い、`info_001`（情報収集）をWeb Agentに指示。
      * Web Agentは検索を実行し、結果をPlanner Agentに返す。
      * Planner AgentはWeb Agentからの結果を評価し、必要に応じて`info_001`の`status`を「完了」に更新し、KVSに保存。
      * `info_001`が完了したことを確認後、Planner Agentは`task_001`（レポート作成）をCasual Agent（または専門Agent）に指示。
      * この際、`task_001`の`need`フィールドに基づいて、Planner Agentは`info_001`で得られた情報をCasual Agentに渡す。
5.  **動的な計画更新と結果評価**:
      * 各タスクの実行後、Planner Agentは結果を評価し、必要に応じてタスクの`status`を更新したり、次のステップを計画したりする。
      * 例えば、レポート作成中に新たな情報が必要になった場合、Planner Agentは動的に新たな情報参照タスクを計画に追加し、実行を指示する。
6.  **ユーザーへのフィードバック**: Planner Agentはタスクの進捗や完了をFrontEndを通じてユーザーに通知。

#### 3\. 「情報がタスクの開始条件となる関係性」の実現

この設計案では、Planner AgentのJSONプランの`"need": ["previous_task_id"]`という既存の仕組みを拡張し、情報参照タスクが通常の作業タスクの前提条件となるように利用します。

  * **情報参照タスクの定義**: `info_reference_schema`に従い、`reference_type`が`KVS_DOCUMENT`で、`kvs_key`がユーザーセッションIDを指すタスクを定義。
  * **前提条件としての指定**: 作業タスクの`"need"`フィールドに、対応する情報参照タスクの`id`を指定。
  * **Planner Agentの役割**: Planner Agentは、作業タスクを実行する前に、`need`で指定された情報参照タスクが完了していることを確認。未完了であれば、その情報参照タスクの実行を優先する。

#### 4\. KVSの活用

  * **ヒアリング結果**: ユーザーの要望や設定の「マスターデータ」として機能。Planner Agentは常にこれを参照して、ユーザーの意図に沿った計画を立てる。
  * **タスクスキーマ**: タスクの「型定義」として機能。Planner Agentはこれに基づいて、各タスクが持つべきフィールドとその制約を理解する。
  * **タスクデータ**: 現在進行中または完了したタスクの「実行データ」として機能。Planner Agentはこれを更新し、ユーザーインターフェースはこれを表示する。


承知いたしました。今回のプロトタイプ設計案を検討するにあたり、AgenticSeekのPlanner Agentに関する以下の情報と概念を参考にしています。

---
## kvsのサンプルコード
```python
from upstash_redis import Redis
import os

redis = Redis(url=os.environ["UPSTASH_URL"], token=os.environ["UPSTASH_TOKEN"])
redis.set("foo", "bar")
value = redis.get("foo")
```

---
## LLMを呼び出すサンプルコード

```python
import dspy
from dotenv import load_dotenv

# Gemini Flash 2.5 configuration
load_dotenv(os.path.expanduser(".env"))
gemini = dspy.LM(
    model="gemini/gemini-2.5-flash",
    temperature=0.0,
    max_tokens=10000,
    num_retries=3,
    cache=True,
)
dspy.settings.configure(lm=gemini)
```
import { Redis } from '@upstash/redis'
const redis = new Redis({
  url: 'https://helping-tapir-50354.upstash.io',
  token: 'AcSyAAIjcDE3YzRmYWRmM2RhMDE0MTQ4YmU1MjhiODUyNTAzNmQzZHAxMA',
})

await redis.set("foo", "bar");
await redis.get("foo");
---

### AgenticSeek の Planner Agent から参考にした箇所

今回の設計案は、AgenticSeekのPlanner Agentが持つ**複雑なタスクの分解能力**と**サブエージェントのオーケストレーション**という主要な概念を基盤としています。具体的には以下の点です。

1.  **JSONベースのタスク計画 (JSON-Based Task Planning)**
    * Planner Agentがタスクの実行計画をJSON形式で構造化するという点。今回の設計案では、ユーザーのタスク管理をこのJSON計画に乗せることで、**「何をするか」「どのようにするかの概要」** を形式的に管理できるようにしました。
    * `id`, `agent`, `task`, `need` といった基本的なフィールド構成は、Planner AgentのJSONプラン構造から直接取り入れています。これにより、タスク間の依存関係を明確に表現することが可能になります。
    * **関連ソースファイル**: `sources/agents/planner_agent.py` (特に`parse_agent_tasks()`、`get_task_names()`関連)

2.  **実行結果の受け渡しと依存関係の解決 (Execution Result Passing and Dependency Resolution)**
    * 各エージェントの実行結果が保存され (`agents_work_result`辞書)、次のタスクのプロンプト生成時に依存するタスクの結果が含まれるという仕組み。
    * これは、特にあなたが重視する**「情報がタスクの開始条件となる関係性」** を実現するために不可欠な概念です。情報参照タスク（例: Planner Agent資料の参照）の完了後、その情報が次の作業タスク（例: レポート作成）のプロンプトに組み込まれることで、エージェントが**「いつ何をするか（情報が揃った後に作業を開始する）」** を適切に判断し、実行できるようになります。
    * **関連ソースファイル**: `sources/agents/planner_agent.py` (特に`get_work_result_agent()`、`make_prompt()`関連)

3.  **動的な計画更新 (Dynamic Plan Updates)**
    * エージェントの実行結果に基づいて計画を再評価し、必要に応じて修正するというPlanner Agentの機能。
    * これにより、タスクの途中で新たな情報収集が必要になったり、計画の見直しが必要になったりした場合でも、システムが自律的に対応できる柔軟性を持たせることが可能です。

4.  **サブエージェント管理 (Sub-Agent Management)**
    * `CoderAgent`, `FileAgent`, `BrowserAgent`, `CasualAgent`といった専門エージェントをPlanner Agentが管理し、適切なエージェントにタスクを割り当てるというアーキテクチャ。
    * 今回のタスク管理システムでも、情報収集には`BrowserAgent`（Web Agent）、データ処理には`CoderAgent`といった形で、タスクの内容に応じて最適なエージェントを活用する枠組みを想定しています。
    * **関連ソースファイル**: `sources/agents/planner_agent.py` (特に`agents`辞書の初期化、`start_agent_process()`関連)

これらの概念を参考に、あなたの具体的なタスク管理の要望（タスクの粒度、状態管理、KVS連携など）に合わせて、Planner Agentのフレームワークを拡張し、カスタマイズする設計を提案しました。

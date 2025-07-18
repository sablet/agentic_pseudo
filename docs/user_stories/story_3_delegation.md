# ストーリー3：複雑な目的のための専門エージェントへの委譲（間接実行）

## 概要

このストーリーでは、複雑で多岐にわたる目的を達成するために、抽象エージェントが複数の専門エージェントに作業を委譲し、その進捗を統合管理する過程を描いています。システム全体の協調によってユーザーの複雑な課題を解決します。

---

## ユーザーストーリー

**目的:** ユーザーは、自身の複雑な目的を達成するために、複数の専門知識や手順を必要とするタスクを、最適な専門エージェントに自動的に委譲し、その進捗を管理したい。

**アクター:** 個人開発者、スタートアップ創業者、システム設計担当者

**シナリオ:**

1.  **複雑な目的の提示:** ユーザーは「ECサイトを構築するための最適な技術スタック全体を選定し、各技術の組み合わせ相性や開発・運用コストも含めて総合的に判断したい」という比較的複雑で多岐にわたる目的を、抽象度の高い「技術スタック選定アシスタント」エージェントに伝える。

2.  **目的の分解と委譲先の推定:** 「技術スタック選定アシスタント」エージェントは、ユーザーの目的を解析し、それを達成するために必要な複数の下位タスク（例: 「フロントエンド技術調査」「バックエンド技術調査」「データベース技術調査」「インフラ・デプロイ技術調査」「決済システム調査」）を識別する。
    * エージェントは、これらの下位タスクそれぞれに対応する、より専門的な「フロントエンド技術比較エージェント」「バックエンド技術比較エージェント」「データベース技術比較エージェント」「クラウドインフラ比較エージェント」「決済システム比較エージェント」といったサブエージェント群をシステム内で推定する。

3.  **委譲の承認と実行:**
    * エージェントは、特定された下位タスクと、それらを処理するのに適したサブエージェントのリストをユーザーに提示し、委譲の承認を求める。
    * ユーザーが承認すると、「技術スタック選定アシスタント」エージェントは、それぞれのサブエージェントに必要なコンテキスト（プロジェクト規模、予想トラフィック、チームスキルレベルなど）と初期データを与え、タスクを自動的に委譲する。
    * 抽象エージェントのステータスは「待ち状態」（または「委譲済み」）に更新される。4.  **サブエージェントによる並行処理と協調:**
    * 委譲された各サブエージェントは、それぞれの専門領域でタスクを実行する。例えば、「フロントエンド技術比較エージェント」はReact/Vue/Angularの比較調査を行い、「バックエンド技術比較エージェント」はNode.js/Python/Goの特徴分析を行う。
    * 必要に応じて、サブエージェント間で情報の受け渡しや連携が行われる。例えば、フロントエンド技術の選択結果がバックエンド技術の推奨に影響を与える。

5.  **進捗の統合と結果の提示:** 各サブエージェントのタスク完了状況は、「技術スタック選定アシスタント」エージェントに集約され、ユーザーは全体的な進捗状況をUI上で確認できる。全てのサブエージェントのタスクが完了すると、「技術スタック選定アシスタント」エージェントは、各サブエージェントからの結果を統合し、最終的な「ECサイト開発のための推奨技術スタック選定レポート」を生成してユーザーに提示する。このレポートには、各技術の相性マトリクス、総合開発コスト見積もり、チーム習得難易度なども含まれる。

---

## 成功判定基準

### 目的の適切な分解と委譲
**基準:** 抽象エージェントが、複雑な目的を論理的に分解し、最適な専門エージェントに正確にタスクを委譲できているか。

**レビューポイント:**
- 分解された下位タスクが、元の複雑な目的を達成するために全て網羅されているか？
- 各下位タスクが、委譲された専門エージェントの機能と専門性に合致しているか？（例: 市場調査タスクが市場調査エージェントに委譲されているか）
- 委譲時に、各サブエージェントに必要なコンテキスト情報やパラメータが正しく引き継がれているか？

### 進捗の可視性と統合
**基準:** ユーザーが、複数のサブエージェントの進捗状況を、抽象エージェントを通じて一元的に、かつリアルタイムに近い形で確認できるか。

**レビューポイント:**
- UI上で、各サブエージェントの個別のステータス（例: 実行中、完了、エラー）と、全体の進捗状況（例: 〇/〇タスク完了）が明確に表示されているか？
- サブエージェントからの結果が、最終的に抽象エージェントによって統合され、一貫性のある最終レポートや成果物として提示されているか？

### 最終成果物の品質
**基準:** 各サブエージェントの成果物が統合された最終成果物が、ユーザーの当初の複雑な目的を完全に達成し、高い品質を持っているか。

**レビューポイント:**
- 最終レポートや提案が、網羅性、論理性、実用性の点で優れているか？
- 各サブエージェント間の連携がスムーズに行われ、不整合や重複がないか？
- ユーザーが、最終成果物を見て「当初の複雑な課題に対する答えが出た」と感じるか？

### エラーハンドリングとリカバリ
**基準:** いずれかのサブエージェントで問題が発生した場合、それが適切に検知され、ユーザーに通知されるか、またはリカバリが試みられるか。

**レビューポイント:**
- サブエージェントのエラーが親エージェントに正しく伝播し、UIに表示されるか？
- エラー発生時に、ユーザーが次のアクション（例: 再実行、別のサブエージェントの選択）を判断できる情報が提供されるか？
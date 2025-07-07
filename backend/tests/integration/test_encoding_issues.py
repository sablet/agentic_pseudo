"""
バックエンドAPIの文字エンコーディング問題を検出するテスト
日本語テキストの文字化けや不正なUnicodeエスケープを検出する
"""

import pytest
import json
import re
from fastapi.testclient import TestClient

from src.api.main import app
from src.repository.kvs_repository import KVSRepository
from src.service.sub_agents import AgentManager

client = TestClient(app)


class TestEncodingIssues:
    """文字エンコーディング問題のテストクラス"""

    def setup_method(self):
        """各テストメソッドの前に実行される設定"""
        self.kvs_repo = KVSRepository()
        self.agent_manager = AgentManager()

    def test_japanese_text_not_corrupted_in_agents_api(self):
        """エージェントAPIで日本語テキストが文字化けしていないことを確認"""
        response = client.get("/api/agents")
        assert response.status_code == 200

        data = response.json()

        # レスポンスの生データをチェック
        response_text = response.text
        print(f"Raw response text: {response_text}")

        # 文字化けパターンを検出
        corrupted_patterns = [
            r"[àáâãäåæçèéêëìíîïñòóôõöøùúûü]",  # 一般的な文字化けパターン
            r"q«\.j",  # 具体的な文字化け例
            r"Á",  # 具体的な文字化け例
            r"~\)\^",  # 具体的な文字化け例
            r"\\u[0-9a-fA-F]{4}",  # Unicodeエスケープシーケンス
        ]

        for pattern in corrupted_patterns:
            matches = re.findall(pattern, response_text)
            if matches:
                pytest.fail(f"文字化けパターン '{pattern}' が検出されました: {matches}")

        # エージェント名が期待される値であることを確認
        expected_agents = ["web", "coder", "casual", "file"]
        assert "agents" in data
        assert "descriptions" in data

        for agent in data["agents"]:
            assert agent in expected_agents, f"予期しないエージェント名: {agent}"
            assert isinstance(agent, str), (
                f"エージェント名が文字列ではありません: {type(agent)}"
            )
            assert agent.isascii(), (
                f"エージェント名にASCII以外の文字が含まれています: {agent}"
            )

        # 説明文の日本語が正しくエンコードされていることを確認
        for agent_key, description in data["descriptions"].items():
            assert isinstance(description, str), (
                f"説明文が文字列ではありません: {type(description)}"
            )
            assert len(description) > 0, f"説明文が空です: {agent_key}"

            # 日本語文字が含まれている場合の確認
            if any(ord(char) > 127 for char in description):
                # 日本語文字が含まれている場合、文字化けしていないことを確認
                assert not re.search(r"[àáâãäåæçèéêëìíîïñòóôõöøùúûü]", description), (
                    f"説明文に文字化けが検出されました: {description}"
                )

    def test_task_data_encoding_integrity(self):
        """タスクデータのエンコーディング整合性をテスト"""
        # セッション作成
        session_response = client.post("/api/sessions")
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]

        # 日本語を含むヒアリング結果を保存
        hearing_data = {
            "session_id": session_id,
            "hearing_result": "営業データの時系列分析を行い、Q4売上予測モデルを構築したい。",
        }
        hearing_response = client.post("/api/hearing", json=hearing_data)
        assert hearing_response.status_code == 200

        # 日本語を含むタスクプランを作成
        task_data = {
            "user_instruction": "営業データの時系列分析を行い、Q4売上予測モデルを構築したい。データ処理から予測、レポート作成まで一貫して対応してください。",
            "session_id": session_id,
        }
        task_response = client.post("/api/tasks/create", json=task_data)
        assert task_response.status_code == 200

        # タスクステータスを取得して文字エンコーディングをチェック
        status_response = client.get(f"/api/tasks/status/{session_id}")
        assert status_response.status_code == 200

        # レスポンスの生データをチェック
        response_text = status_response.text
        print(f"Task status raw response: {response_text}")

        # 文字化けパターンを検出
        corrupted_patterns = [
            r'ã[^"]*',  # ãで始まる文字化けパターン
            r"q«\.j",  # 具体的な文字化け例
            r"Á",  # 具体的な文字化け例
            r"~\)\^",  # 具体的な文字化け例
        ]

        for pattern in corrupted_patterns:
            matches = re.findall(pattern, response_text)
            if matches:
                pytest.fail(
                    f"タスクデータで文字化けパターン '{pattern}' が検出されました: {matches}"
                )

        data = status_response.json()
        if data.get("task_data"):
            task_data = data["task_data"]

            # 日次タスクのエンコーディングチェック
            if task_data.get("daily_tasks"):
                for task in task_data["daily_tasks"]:
                    self._check_task_encoding(task)

            # 情報参照タスクのエンコーディングチェック
            if task_data.get("info_references"):
                for task in task_data["info_references"]:
                    self._check_task_encoding(task)

    def _check_task_encoding(self, task: dict):
        """個別タスクのエンコーディングをチェック"""
        # エージェント名のチェック
        if "agent" in task:
            agent = task["agent"]
            expected_agents = ["web", "coder", "casual", "file"]

            # エージェント名が期待される値の一つであることを確認
            assert agent in expected_agents, (
                f"予期しないエージェント名: '{agent}' (type: {type(agent)})"
            )
            assert agent.isascii(), (
                f"エージェント名にASCII以外の文字が含まれています: '{agent}'"
            )

        # タスク名のチェック
        if "task" in task:
            task_name = task["task"]
            assert isinstance(task_name, str), (
                f"タスク名が文字列ではありません: {type(task_name)}"
            )
            assert len(task_name) > 0, f"タスク名が空です"

            # 文字化けパターンの検出
            corrupted_patterns = [
                r'ã[^"]*',  # ãで始まる文字化けパターン
                r"[àáâãäåæçèéêëìíîïñòóôõöøùúûü]",  # 一般的な文字化けパターン
            ]

            for pattern in corrupted_patterns:
                matches = re.findall(pattern, task_name)
                if matches:
                    pytest.fail(
                        f"タスク名で文字化けパターン '{pattern}' が検出されました: '{task_name}', matches: {matches}"
                    )

        # ステータスのチェック
        if "status" in task:
            status = task["status"]
            expected_statuses = [
                "pending",
                "in_progress",
                "completed",
                "failed",
                "未着手",
                "実行中",
                "完了",
                "失敗",
            ]

            # ステータスが期待される値の一つであることを確認
            if status not in expected_statuses:
                # 文字化けの可能性をチェック
                corrupted_patterns = [
                    r"[àáâãäåæçèéêëìíîïñòóôõöøùúûü]",  # 一般的な文字化けパターン
                ]

                for pattern in corrupted_patterns:
                    if re.search(pattern, status):
                        pytest.fail(
                            f"ステータスで文字化けパターン '{pattern}' が検出されました: '{status}'"
                        )

                # 文字化けパターンが見つからない場合は警告
                print(
                    f"警告: 予期しないステータス値: '{status}' (type: {type(status)})"
                )

    def test_unicode_escape_sequences_not_present(self):
        """レスポンスにUnicodeエスケープシーケンスが含まれていないことを確認"""
        # エージェントAPIをテスト
        response = client.get("/api/agents")
        response_text = response.text

        # \uXXXXパターンを検出
        unicode_escapes = re.findall(r"\\u[0-9a-fA-F]{4}", response_text)
        if unicode_escapes:
            pytest.fail(
                f"レスポンスにUnicodeエスケープシーケンスが含まれています: {unicode_escapes}"
            )

        # エンコードされた日本語文字の検出
        encoded_japanese_patterns = [
            r"\\u3042-\\u3096",  # ひらがな
            r"\\u30A0-\\u30FF",  # カタカナ
            r"\\u4E00-\\u9FAF",  # 漢字
        ]

        for pattern in encoded_japanese_patterns:
            matches = re.findall(pattern, response_text)
            if matches:
                pytest.fail(
                    f"レスポンスにエンコードされた日本語文字が含まれています: {matches}"
                )

    def test_content_type_header_includes_utf8(self):
        """Content-TypeヘッダーにUTF-8が含まれていることを確認"""
        response = client.get("/api/agents")
        content_type = response.headers.get("content-type", "")

        # application/jsonが含まれていることを確認
        assert "application/json" in content_type, (
            f"Content-Typeにapplication/jsonが含まれていません: {content_type}"
        )

        # charset=utf-8が含まれていることを確認（推奨）
        if "charset" in content_type:
            assert "utf-8" in content_type.lower(), (
                f"Content-Typeにutf-8が含まれていません: {content_type}"
            )
        else:
            print(f"警告: Content-Typeにcharsetが指定されていません: {content_type}")


if __name__ == "__main__":
    # 直接実行する場合のテストコード
    test_instance = TestEncodingIssues()
    test_instance.setup_method()

    print("=== エージェントAPIのエンコーディングテスト ===")
    test_instance.test_japanese_text_not_corrupted_in_agents_api()
    print("✅ エージェントAPIテスト完了")

    print("\n=== タスクデータのエンコーディングテスト ===")
    test_instance.test_task_data_encoding_integrity()
    print("✅ タスクデータテスト完了")

    print("\n=== Unicodeエスケープシーケンステスト ===")
    test_instance.test_unicode_escape_sequences_not_present()
    print("✅ Unicodeエスケープテスト完了")

    print("\n=== Content-Typeヘッダーテスト ===")
    test_instance.test_content_type_header_includes_utf8()
    print("✅ Content-Typeテスト完了")

    print("\n🎉 全てのエンコーディングテストが完了しました")

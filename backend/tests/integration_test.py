#!/usr/bin/env python3
"""
統合テストスクリプト

このスクリプトは、バックエンドAPIの統合テストを自動化します。

使用方法:
    python integration_test.py

環境変数:
    BACKEND_URL: バックエンドAPIのベースURL（デフォルト: http://localhost:8000）
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid


class Colors:
    """ターミナル出力用のカラーコード"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class IntegrationTestRunner:
    """統合テストランナー"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.test_user_id: Optional[str] = None
        self.test_username: str = f"test_user_{uuid.uuid4().hex[:8]}"

        # テスト結果カウンター
        self.passed = 0
        self.failed = 0
        self.test_results: List[Tuple[str, bool, str]] = []

    def log_info(self, message: str):
        """情報ログを出力"""
        print(f"{Colors.BLUE}ℹ{Colors.RESET}  {message}")

    def log_success(self, message: str):
        """成功ログを出力"""
        print(f"{Colors.GREEN}✓{Colors.RESET}  {message}")

    def log_error(self, message: str):
        """エラーログを出力"""
        print(f"{Colors.RED}✗{Colors.RESET}  {message}")

    def log_warning(self, message: str):
        """警告ログを出力"""
        print(f"{Colors.YELLOW}⚠{Colors.RESET}  {message}")

    def assert_test(self, test_name: str, condition: bool, error_message: str = ""):
        """テスト結果をアサート"""
        if condition:
            self.passed += 1
            self.log_success(f"{test_name}: PASSED")
            self.test_results.append((test_name, True, ""))
        else:
            self.failed += 1
            self.log_error(f"{test_name}: FAILED - {error_message}")
            self.test_results.append((test_name, False, error_message))

    def test_health_check(self):
        """ヘルスチェックエンドポイントをテスト"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.assert_test(
                "Health Check",
                response.status_code == 200,
                f"Expected 200, got {response.status_code}"
            )
        except Exception as e:
            self.assert_test("Health Check", False, str(e))

    def test_user_signup(self):
        """ユーザー登録エンドポイントをテスト"""
        try:
            payload = {
                "username": self.test_username,
                "email": f"{self.test_username}@example.com",
                "kategori": "学生",
                "gakuseki_bango": "S99999",
                "password": "testpassword123"
            }
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json=payload,
                timeout=5
            )

            success = response.status_code == 201
            if success:
                data = response.json()
                self.test_user_id = data.get("id")

            self.assert_test(
                "User Signup",
                success,
                f"Expected 201, got {response.status_code}: {response.text}"
            )
        except Exception as e:
            self.assert_test("User Signup", False, str(e))

    def test_user_login(self):
        """ユーザーログインエンドポイントをテスト"""
        try:
            payload = {
                "username": self.test_username,
                "password": "testpassword123"
            }
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=payload,
                timeout=5
            )

            success = response.status_code == 200
            if success:
                data = response.json()
                self.access_token = data.get("access_token")

            self.assert_test(
                "User Login",
                success and self.access_token is not None,
                f"Expected 200 with access_token, got {response.status_code}"
            )
        except Exception as e:
            self.assert_test("User Login", False, str(e))

    def test_get_current_user(self):
        """現在のユーザー情報取得エンドポイントをテスト"""
        if not self.access_token:
            self.assert_test("Get Current User", False, "No access token available")
            return

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=headers,
                timeout=5
            )

            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("username") == self.test_username

            self.assert_test(
                "Get Current User",
                success,
                f"Expected 200 with correct username, got {response.status_code}"
            )
        except Exception as e:
            self.assert_test("Get Current User", False, str(e))

    def test_wiki_list(self):
        """Wikiページ一覧取得エンドポイントをテスト"""
        if not self.access_token:
            self.assert_test("Wiki Page List", False, "No access token available")
            return

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(
                f"{self.base_url}/wiki/pages",
                headers=headers,
                timeout=5
            )

            success = response.status_code == 200

            self.assert_test(
                "Wiki Page List",
                success,
                f"Expected 200, got {response.status_code}"
            )
        except Exception as e:
            self.assert_test("Wiki Page List", False, str(e))

    def test_wiki_create(self):
        """Wikiページ作成エンドポイントをテスト"""
        if not self.access_token:
            self.assert_test("Wiki Page Create", False, "No access token available")
            return

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            payload = {
                "title": f"Test Wiki Page {datetime.now().isoformat()}",
                "content": "This is an automated test wiki page."
            }
            response = requests.post(
                f"{self.base_url}/wiki/pages",
                headers=headers,
                json=payload,
                timeout=5
            )

            success = response.status_code == 201
            if success:
                data = response.json()
                success = "id" in data and "title" in data

            self.assert_test(
                "Wiki Page Create",
                success,
                f"Expected 201 with id and title, got {response.status_code}"
            )
        except Exception as e:
            self.assert_test("Wiki Page Create", False, str(e))

    def test_tags_list(self):
        """タグ一覧取得エンドポイントをテスト"""
        if not self.access_token:
            self.assert_test("Tags List", False, "No access token available")
            return

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(
                f"{self.base_url}/tags",
                headers=headers,
                timeout=5
            )

            success = response.status_code == 200

            self.assert_test(
                "Tags List",
                success,
                f"Expected 200, got {response.status_code}"
            )
        except Exception as e:
            self.assert_test("Tags List", False, str(e))

    def test_tag_create(self):
        """タグ作成エンドポイントをテスト"""
        if not self.access_token:
            self.assert_test("Tag Create", False, "No access token available")
            return

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            payload = {
                "name": f"Test Tag {uuid.uuid4().hex[:6]}"
            }
            response = requests.post(
                f"{self.base_url}/tags",
                headers=headers,
                json=payload,
                timeout=5
            )

            success = response.status_code == 201
            if success:
                data = response.json()
                success = "id" in data and "name" in data

            self.assert_test(
                "Tag Create",
                success,
                f"Expected 201 with id and name, got {response.status_code}"
            )
        except Exception as e:
            self.assert_test("Tag Create", False, str(e))

    def test_search(self):
        """統合検索エンドポイントをテスト"""
        if not self.access_token:
            self.assert_test("Search", False, "No access token available")
            return

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(
                f"{self.base_url}/search",
                headers=headers,
                params={"q": "test", "type": "all"},
                timeout=5
            )

            success = response.status_code == 200
            if success:
                data = response.json()
                success = "results" in data and "total" in data

            self.assert_test(
                "Search",
                success,
                f"Expected 200 with results and total, got {response.status_code}"
            )
        except Exception as e:
            self.assert_test("Search", False, str(e))

    def print_summary(self):
        """テスト結果のサマリーを出力"""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}統合テスト結果サマリー{Colors.RESET}")
        print("=" * 70)

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\n合計テスト数: {total}")
        print(f"{Colors.GREEN}成功: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}失敗: {self.failed}{Colors.RESET}")
        print(f"成功率: {pass_rate:.1f}%")

        if self.failed > 0:
            print(f"\n{Colors.BOLD}失敗したテスト:{Colors.RESET}")
            for test_name, passed, error_msg in self.test_results:
                if not passed:
                    print(f"  {Colors.RED}✗{Colors.RESET} {test_name}: {error_msg}")

        print("\n" + "=" * 70)

        # 終了コード
        return 0 if self.failed == 0 else 1

    def run_all_tests(self):
        """すべてのテストを実行"""
        print(f"\n{Colors.BOLD}統合テスト開始{Colors.RESET}")
        print(f"Backend URL: {self.base_url}")
        print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")

        # ヘルスチェック
        self.log_info("ヘルスチェック...")
        self.test_health_check()

        # 認証系テスト
        self.log_info("\n認証APIテスト...")
        self.test_user_signup()
        self.test_user_login()
        self.test_get_current_user()

        # Wiki API テスト
        self.log_info("\nWiki APIテスト...")
        self.test_wiki_list()
        self.test_wiki_create()

        # Tags API テスト
        self.log_info("\nTags APIテスト...")
        self.test_tags_list()
        self.test_tag_create()

        # Search API テスト
        self.log_info("\nSearch APIテスト...")
        self.test_search()

        # サマリー出力
        return self.print_summary()


def main():
    """メイン関数"""
    # 環境変数からバックエンドURLを取得
    backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")

    # テストランナーを作成して実行
    runner = IntegrationTestRunner(backend_url)

    try:
        exit_code = runner.run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}テストが中断されました{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}予期しないエラーが発生しました: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()

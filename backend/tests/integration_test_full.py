"""
統合テストスクリプト（完全版）

pytest対応の統合テストスイート。全APIエンドポイントをテストします。

実行方法:
    # Docker内で実行
    docker exec finalwork-backend-1 pytest tests/integration_test_full.py -v

    # ローカルで実行
    pytest tests/integration_test_full.py -v

環境変数:
    BACKEND_URL: バックエンドAPIのベースURL（デフォルト: http://localhost:8000）
"""

import pytest
import requests
import uuid
from typing import Dict, Optional


# テストデータ
TEST_USER = {
    "username": f"test_user_{uuid.uuid4().hex[:8]}",
    "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
    "kategori": "学生",
    "gakuseki_bango": "S99999",
    "password": "testpassword123"
}

TEST_USER_2 = {
    "username": f"test_user2_{uuid.uuid4().hex[:8]}",
    "email": f"test2_{uuid.uuid4().hex[:8]}@example.com",
    "kategori": "教員",
    "password": "testpassword456"
}


@pytest.fixture(scope="module")
def base_url():
    """ベースURLを取得"""
    import os
    return os.environ.get("BACKEND_URL", "http://localhost:8000")


@pytest.fixture(scope="module")
def auth_tokens(base_url):
    """認証トークンを取得（テストユーザー作成とログイン）"""
    # ユーザー1を作成
    response = requests.post(
        f"{base_url}/auth/signup",
        json=TEST_USER
    )
    assert response.status_code == 201, f"User 1 signup failed: {response.text}"
    user1_data = response.json()

    # ユーザー1でログイン
    response = requests.post(
        f"{base_url}/auth/login",
        json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    assert response.status_code == 200, f"User 1 login failed: {response.text}"
    user1_token = response.json()["access_token"]

    # ユーザー2を作成
    response = requests.post(
        f"{base_url}/auth/signup",
        json=TEST_USER_2
    )
    assert response.status_code == 201, f"User 2 signup failed: {response.text}"
    user2_data = response.json()

    # ユーザー2でログイン
    response = requests.post(
        f"{base_url}/auth/login",
        json={
            "username": TEST_USER_2["username"],
            "password": TEST_USER_2["password"]
        }
    )
    assert response.status_code == 200, f"User 2 login failed: {response.text}"
    user2_token = response.json()["access_token"]

    return {
        "user1": {"token": user1_token, "id": user1_data["id"], "username": TEST_USER["username"]},
        "user2": {"token": user2_token, "id": user2_data["id"], "username": TEST_USER_2["username"]}
    }


class TestHealthCheck:
    """ヘルスチェックエンドポイントのテスト"""

    def test_health_check(self, base_url):
        """ヘルスチェックが成功すること"""
        response = requests.get(f"{base_url}/health")
        assert response.status_code == 200


class TestAuth:
    """認証APIのテスト"""

    def test_signup(self, base_url):
        """新規ユーザー登録が成功すること"""
        test_user = {
            "username": f"signup_test_{uuid.uuid4().hex[:8]}",
            "email": f"signup_{uuid.uuid4().hex[:8]}@example.com",
            "kategori": "学生",
            "gakuseki_bango": "S88888",
            "password": "password123"
        }
        response = requests.post(f"{base_url}/auth/signup", json=test_user)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["username"] == test_user["username"]

    def test_login(self, base_url, auth_tokens):
        """ログインが成功すること"""
        # auth_tokensフィクスチャで既にログイン済み
        assert auth_tokens["user1"]["token"] is not None
        assert auth_tokens["user2"]["token"] is not None

    def test_get_current_user(self, base_url, auth_tokens):
        """認証ユーザー情報取得が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(f"{base_url}/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == auth_tokens["user1"]["username"]


class TestWiki:
    """Wiki APIのテスト"""

    @pytest.fixture(scope="class")
    def wiki_page(self, base_url, auth_tokens):
        """テスト用Wikiページを作成"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        page_data = {
            "title": f"Test Wiki Page {uuid.uuid4().hex[:6]}",
            "content": "This is a test wiki page for integration testing."
        }
        response = requests.post(
            f"{base_url}/wiki/pages",
            headers=headers,
            json=page_data
        )
        assert response.status_code == 201
        return response.json()

    def test_create_wiki_page(self, base_url, auth_tokens):
        """Wikiページ作成が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        page_data = {
            "title": f"Create Test {uuid.uuid4().hex[:6]}",
            "content": "Test content"
        }
        response = requests.post(
            f"{base_url}/wiki/pages",
            headers=headers,
            json=page_data
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == page_data["title"]

    def test_get_wiki_pages(self, base_url, auth_tokens, wiki_page):
        """Wikiページ一覧取得が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(f"{base_url}/wiki/pages", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_wiki_page_detail(self, base_url, auth_tokens, wiki_page):
        """Wikiページ詳細取得が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(
            f"{base_url}/wiki/pages/{wiki_page['id']}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == wiki_page["id"]
        assert data["title"] == wiki_page["title"]

    def test_update_wiki_page(self, base_url, auth_tokens, wiki_page):
        """Wikiページ更新が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        update_data = {
            "title": "Updated Title",
            "content": "Updated content"
        }
        response = requests.put(
            f"{base_url}/wiki/pages/{wiki_page['id']}",
            headers=headers,
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]

    def test_share_wiki_page(self, base_url, auth_tokens, wiki_page):
        """Wikiページ共有が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        share_data = {
            "user_id": auth_tokens["user2"]["id"],
            "permission_level": "VIEW_ONLY"
        }
        response = requests.post(
            f"{base_url}/wiki/pages/{wiki_page['id']}/share",
            headers=headers,
            json=share_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True


class TestTags:
    """タグAPIのテスト"""

    @pytest.fixture(scope="class")
    def tag(self, base_url, auth_tokens):
        """テスト用タグを作成"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        tag_data = {
            "name": f"Test Tag {uuid.uuid4().hex[:6]}"
        }
        response = requests.post(
            f"{base_url}/tags",
            headers=headers,
            json=tag_data
        )
        assert response.status_code == 201
        return response.json()

    def test_create_tag(self, base_url, auth_tokens):
        """タグ作成が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        tag_data = {
            "name": f"Create Test Tag {uuid.uuid4().hex[:6]}"
        }
        response = requests.post(
            f"{base_url}/tags",
            headers=headers,
            json=tag_data
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == tag_data["name"]

    def test_get_tags(self, base_url, auth_tokens, tag):
        """タグ一覧取得が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(f"{base_url}/tags", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_tag_detail(self, base_url, auth_tokens, tag):
        """タグ詳細取得が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(
            f"{base_url}/tags/{tag['id']}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tag["id"]
        assert data["name"] == tag["name"]

    def test_assign_tag(self, base_url, auth_tokens, tag):
        """タグ割り当てが成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        assign_data = {
            "user_id": auth_tokens["user2"]["id"]
        }
        response = requests.post(
            f"{base_url}/tags/{tag['id']}/assign",
            headers=headers,
            json=assign_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_delete_tag(self, base_url, auth_tokens):
        """タグ削除が成功すること（作成者のみ）"""
        # 削除用の新しいタグを作成
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        tag_data = {
            "name": f"Delete Test Tag {uuid.uuid4().hex[:6]}"
        }
        response = requests.post(
            f"{base_url}/tags",
            headers=headers,
            json=tag_data
        )
        assert response.status_code == 201
        tag = response.json()

        # タグを削除
        response = requests.delete(
            f"{base_url}/tags/{tag['id']}",
            headers=headers
        )
        assert response.status_code == 204


class TestSearch:
    """検索APIのテスト"""

    def test_search_all(self, base_url, auth_tokens):
        """統合検索（全タイプ）が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(
            f"{base_url}/search",
            headers=headers,
            params={"q": "test", "type": "all"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data

    def test_search_wiki(self, base_url, auth_tokens):
        """Wiki検索が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(
            f"{base_url}/search",
            headers=headers,
            params={"q": "test", "type": "wiki"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data


class TestChannels:
    """チャンネルAPIのテスト"""

    @pytest.fixture(scope="class")
    def channel(self, base_url, auth_tokens):
        """テスト用チャンネルを作成"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        channel_data = {
            "name": f"test-channel-{uuid.uuid4().hex[:6]}",
            "description": "Test channel for integration testing",
            "is_private": False
        }
        response = requests.post(
            f"{base_url}/channels",
            headers=headers,
            json=channel_data
        )
        assert response.status_code == 201
        return response.json()

    def test_create_channel(self, base_url, auth_tokens):
        """チャンネル作成が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        channel_data = {
            "name": f"create-test-{uuid.uuid4().hex[:6]}",
            "description": "Create test channel",
            "is_private": False
        }
        response = requests.post(
            f"{base_url}/channels",
            headers=headers,
            json=channel_data
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == channel_data["name"]

    def test_get_channels(self, base_url, auth_tokens, channel):
        """チャンネル一覧取得が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(f"{base_url}/channels", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_channel_detail(self, base_url, auth_tokens, channel):
        """チャンネル詳細取得が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(
            f"{base_url}/channels/{channel['id']}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == channel["id"]
        assert data["name"] == channel["name"]

    def test_send_channel_message(self, base_url, auth_tokens, channel):
        """チャンネルメッセージ送信が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        message_data = {
            "content": "Test message for integration testing"
        }
        response = requests.post(
            f"{base_url}/channels/{channel['id']}/messages",
            headers=headers,
            json=message_data
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["content"] == message_data["content"]

    def test_get_channel_messages(self, base_url, auth_tokens, channel):
        """チャンネルメッセージ一覧取得が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(
            f"{base_url}/channels/{channel['id']}/messages",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestDM:
    """DM APIのテスト"""

    def test_send_dm_message(self, base_url, auth_tokens):
        """DMメッセージ送信が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        message_data = {
            "receiver_id": auth_tokens["user2"]["id"],
            "content": "Test DM message"
        }
        response = requests.post(
            f"{base_url}/messages/dm",
            headers=headers,
            json=message_data
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["content"] == message_data["content"]

    def test_get_dm_conversations(self, base_url, auth_tokens):
        """DM会話一覧取得が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        response = requests.get(
            f"{base_url}/messages/dm",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_dm_messages(self, base_url, auth_tokens):
        """DM特定のメッセージ一覧取得が成功すること"""
        headers = {"Authorization": f"Bearer {auth_tokens['user1']['token']}"}
        partner_id = auth_tokens["user2"]["id"]
        response = requests.get(
            f"{base_url}/messages/dm/{partner_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# テスト実行時の設定
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

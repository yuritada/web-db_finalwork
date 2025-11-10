"""
Search functionality tests (検索機能テスト)

Tests for:
- Wiki search by title and content
- Tag search by name
- User search by username and email
- Cross-type search (all)
"""
import pytest
from fastapi import status


def test_search_wiki_by_title(client, db, test_user):
    """Wiki検索: タイトルで検索"""
    # Login and create wiki page
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/wiki/pages",
        json={"title": "Python Programming Guide", "content": "Learn Python"}
    )

    # Search by title keyword
    search_response = client.get("/search?q=Python&type=wiki")

    assert search_response.status_code == status.HTTP_200_OK
    data = search_response.json()
    assert data["total"] >= 1
    assert any("Python" in result.get("title", "") for result in data["results"])


def test_search_wiki_by_content(client, db, test_user):
    """Wiki検索: 本文で検索"""
    # Login and create wiki page
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/wiki/pages",
        json={"title": "Guide", "content": "This is a comprehensive JavaScript tutorial"}
    )

    # Search by content keyword
    search_response = client.get("/search?q=JavaScript&type=wiki")

    assert search_response.status_code == status.HTTP_200_OK
    data = search_response.json()
    assert data["total"] >= 1


def test_search_tag_by_name(client, db, test_user):
    """タグ検索: タグ名で検索"""
    # Login and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    client.post("/tags", json={"name": "Django Framework"})

    # Search by tag name
    search_response = client.get("/search?q=Django&type=tag")

    assert search_response.status_code == status.HTTP_200_OK
    data = search_response.json()
    assert data["total"] >= 1
    assert any("Django" in result.get("name", "") for result in data["results"])


def test_search_user_by_username(client, db, test_user):
    """ユーザー検索: ユーザー名で検索"""
    # Login
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Search by username
    search_response = client.get(f"/search?q={test_user.username}&type=user")

    assert search_response.status_code == status.HTTP_200_OK
    data = search_response.json()
    assert data["total"] >= 1
    assert any(test_user.username in result.get("username", "") for result in data["results"])


def test_search_user_by_email(client, db, test_user):
    """ユーザー検索: メールアドレスで検索"""
    # Login
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Search by email (partial match)
    search_response = client.get("/search?q=test&type=user")

    assert search_response.status_code == status.HTTP_200_OK
    data = search_response.json()
    assert data["total"] >= 1


def test_search_all_types(client, db, test_user):
    """全タイプ横断検索"""
    # Login
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Create wiki, tag with common keyword
    keyword = "SearchTest"
    client.post(
        "/wiki/pages",
        json={"title": f"{keyword} Wiki", "content": "Content"}
    )
    client.post("/tags", json={"name": f"{keyword} Tag"})

    # Search all types
    search_response = client.get(f"/search?q={keyword}&type=all")

    assert search_response.status_code == status.HTTP_200_OK
    data = search_response.json()
    # Should find at least wiki and tag
    assert data["total"] >= 2

    result_types = [result["type"] for result in data["results"]]
    assert "wiki" in result_types
    assert "tag" in result_types


def test_search_empty_query(client, db, test_user):
    """空の検索クエリ"""
    # Login
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Search with very short query (should fail validation)
    search_response = client.get("/search?q=&type=all")

    # Expecting validation error for empty query
    assert search_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_search_no_results(client, db, test_user):
    """検索結果なし"""
    # Login
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Search for nonexistent keyword
    search_response = client.get("/search?q=NonexistentKeyword12345&type=all")

    assert search_response.status_code == status.HTTP_200_OK
    data = search_response.json()
    assert data["total"] == 0
    assert data["results"] == []


def test_search_case_insensitive(client, db, test_user):
    """検索は大文字小文字を区別しない"""
    # Login and create wiki
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/wiki/pages",
        json={"title": "UPPERCASE Title", "content": "Content"}
    )

    # Search with lowercase
    search_response = client.get("/search?q=uppercase&type=wiki")

    assert search_response.status_code == status.HTTP_200_OK
    data = search_response.json()
    assert data["total"] >= 1


def test_search_requires_authentication(client):
    """検索は認証が必要"""
    # Try to search without authentication
    search_response = client.get("/search?q=test&type=all")

    assert search_response.status_code == status.HTTP_401_UNAUTHORIZED

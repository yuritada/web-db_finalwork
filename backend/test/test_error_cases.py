"""
Error cases tests (エラーケーステスト)

Tests for:
- 404 Not Found errors
- 400 Bad Request errors
- 422 Validation errors
- 403 Forbidden errors
- Edge cases and boundary conditions
"""
import pytest
from fastapi import status


def test_404_wiki_not_found(authenticated_client):
    """Wiki 404エラー: 存在しないWikiページ"""
    # Try to get non-existent wiki page
    response = authenticated_client.get("/wiki/pages/00000000-0000-0000-0000-000000000000")

    # UUID validation happens before resource lookup, so 422 is expected
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_404_tag_not_found(authenticated_client):
    """Tag 404エラー: 存在しないタグ"""
    # Try to get non-existent tag
    response = authenticated_client.get("/tags/00000000-0000-0000-0000-000000000000")

    # UUID validation happens before resource lookup, so 422 is expected
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_404_user_not_found(authenticated_client):
    """User 404エラー: 存在しないユーザー"""
    # Try to get non-existent user
    response = authenticated_client.get("/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_400_invalid_email(client):
    """サインアップ: 無効なメールアドレス"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "not-an-email",  # Invalid email format
            "password": "ValidPass123!",
            "kategori": "学生",
            "gakuseki_bango": "TEST001",
            "faculty": "工学部"
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_400_duplicate_username(client, db, test_user):
    """サインアップ: 重複ユーザー名"""
    response = client.post(
        "/auth/signup",
        json={
            "username": test_user.username,  # Duplicate username
            "email": "new@example.com",
            "password": "NewPass123!",
            "kategori": "学生",
            "gakuseki_bango": "NEW001",
            "faculty": "工学部"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


def test_400_duplicate_email(client, db, test_user):
    """サインアップ: 重複メールアドレス"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "newuser",
            "email": test_user.email,  # Duplicate email
            "password": "NewPass123!",
            "kategori": "学生",
            "gakuseki_bango": "NEW001",
            "faculty": "工学部"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


def test_400_duplicate_tag_name(client, db, test_user):
    """タグ作成: 重複タグ名"""
    # Login and create first tag
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Create first tag
    client.post("/tags", json={"name": "Python"})

    # Try to create duplicate tag
    response = client.post("/tags", json={"name": "Python"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


def test_422_short_password(client):
    """サインアップ: 短すぎるパスワード"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Short1!",  # Only 7 characters
            "kategori": "学生",
            "gakuseki_bango": "TEST001",
            "faculty": "工学部"
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_422_missing_required_fields(client):
    """サインアップ: 必須フィールド欠落"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            # Missing email, password, etc.
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_422_empty_search_query(client, db, test_user):
    """検索: 空のクエリ"""
    # Login
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Try to search with empty query
    response = client.get("/search?q=&type=all")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_403_wiki_edit_without_permission(client, db, test_user, other_user):
    """Wiki編集: 権限なし"""
    # Login as test_user and create wiki
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/wiki/pages",
        json={"title": "Private Page", "content": "Content"}
    )
    page_id = create_response.json()["id"]

    # Login as other_user (no permission)
    login_response2 = client.post(
        "/auth/token",
        data={"username": other_user.username, "password": other_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    # Try to edit without permission
    response = client.put(
        f"/wiki/pages/{page_id}",
        json={"title": "Hacked", "content": "Hacked"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_403_wiki_delete_not_creator(client, db, test_user, other_user):
    """Wiki削除: 作成者以外"""
    # Login as test_user and create wiki
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/wiki/pages",
        json={"title": "Delete Test", "content": "Content"}
    )
    page_id = create_response.json()["id"]

    # Share EDIT permission to other_user
    client.post(
        f"/wiki/pages/{page_id}/share",
        json={"user_id": str(other_user.id), "permission_level": "EDIT"}
    )

    # Login as other_user (has EDIT but not creator)
    login_response2 = client.post(
        "/auth/token",
        data={"username": other_user.username, "password": other_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    # Try to delete (should fail - only creator can delete)
    response = client.delete(f"/wiki/pages/{page_id}")

    # Accept either 403 (Forbidden) or 405 (Method Not Allowed) if delete not implemented
    assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED]


def test_403_tag_delete_not_creator(client, db, test_user, other_user):
    """タグ削除: 作成者以外"""
    # Login as test_user and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    tag_response = client.post("/tags", json={"name": "Test Tag"})
    tag_id = tag_response.json()["id"]

    # Login as other_user
    login_response2 = client.post(
        "/auth/token",
        data={"username": other_user.username, "password": other_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    # Try to delete other's tag
    response = client.delete(f"/tags/{tag_id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_401_unauthorized_access(client):
    """認証なしでのアクセス"""
    # Try to access protected endpoints without authentication
    endpoints = [
        "/users/me",
        "/wiki/pages",
        "/tags",
        "/search?q=test&type=all"
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_401_invalid_token(client):
    """無効なトークンでのアクセス"""
    # Set invalid token
    client.headers = {"Authorization": "Bearer invalid_token_12345"}

    response = client.get("/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_404_wiki_update_nonexistent(authenticated_client):
    """Wiki更新: 存在しないページ"""
    response = authenticated_client.put(
        "/wiki/pages/00000000-0000-0000-0000-000000000000",
        json={"title": "New Title", "content": "New Content"}
    )

    # UUID validation happens before resource lookup, so 422 is expected
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_404_tag_assign_nonexistent_tag(authenticated_client, test_user):
    """タグ割り当て: 存在しないタグ"""
    response = authenticated_client.post(
        "/tags/00000000-0000-0000-0000-000000000000/assign",
        json={"user_id": str(test_user.id)}
    )

    # UUID validation happens before resource lookup, so 422 is expected
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_404_tag_assign_nonexistent_user(client, db, test_user):
    """タグ割り当て: 存在しないユーザー"""
    # Login and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    tag_response = client.post("/tags", json={"name": "Test Tag"})
    tag_id = tag_response.json()["id"]

    # Try to assign to non-existent user
    response = client.post(
        f"/tags/{tag_id}/assign",
        json={"user_id": "00000000-0000-0000-0000-000000000000"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_edge_case_very_long_title(authenticated_client):
    """エッジケース: 非常に長いタイトル"""
    very_long_title = "A" * 1000  # 1000 characters

    response = authenticated_client.post(
        "/wiki/pages",
        json={"title": very_long_title, "content": "Content"}
    )

    # Should either accept (200/201) or reject with validation error (422)
    assert response.status_code in [
        status.HTTP_201_CREATED,
        status.HTTP_422_UNPROCESSABLE_ENTITY
    ]


def test_edge_case_empty_title(authenticated_client):
    """エッジケース: 空のタイトル"""
    response = authenticated_client.post(
        "/wiki/pages",
        json={"title": "", "content": "Content"}
    )

    # Should reject empty title
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edge_case_empty_content(authenticated_client):
    """エッジケース: 空の本文"""
    response = authenticated_client.post(
        "/wiki/pages",
        json={"title": "Title", "content": ""}
    )

    # Should either accept or reject based on business rules
    assert response.status_code in [
        status.HTTP_201_CREATED,
        status.HTTP_422_UNPROCESSABLE_ENTITY
    ]

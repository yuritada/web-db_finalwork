"""
Authentication flow tests (認証フローテスト)

Tests for:
- User registration (signup)
- User login (token generation)
- Getting current user info
- Authentication error cases
"""
import pytest
from fastapi import status


def test_signup_success(client, db):
    """新規ユーザー登録成功"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPass123!",
            "kategori": "学生",
            "gakuseki_bango": "NEW001",
            "faculty": "工学部"
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["kategori"] == "学生"
    assert data["gakuseki_bango"] == "NEW001"
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned


def test_signup_duplicate_username(client, db, test_user):
    """サインアップ失敗: 重複ユーザー名"""
    response = client.post(
        "/auth/signup",
        json={
            "username": test_user.username,  # Duplicate username
            "email": "different@example.com",
            "password": "NewPass123!",
            "kategori": "学生",
            "gakuseki_bango": "DUP001",
            "faculty": "工学部"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


def test_signup_duplicate_email(client, db, test_user):
    """サインアップ失敗: 重複メールアドレス"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "differentuser",
            "email": test_user.email,  # Duplicate email
            "password": "NewPass123!",
            "kategori": "学生",
            "gakuseki_bango": "DUP002",
            "faculty": "工学部"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


def test_signup_invalid_email(client, db):
    """サインアップ失敗: 無効なメールアドレス"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "invaliduser",
            "email": "invalid-email",  # Invalid email format
            "password": "NewPass123!",
            "kategori": "学生",
            "gakuseki_bango": "INV001",
            "faculty": "工学部"
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_short_password(client, db):
    """サインアップ失敗: 短すぎるパスワード（8文字未満）"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "shortpass",
            "email": "short@example.com",
            "password": "Short1!",  # Only 7 characters
            "kategori": "学生",
            "gakuseki_bango": "SHORT01",
            "faculty": "工学部"
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_teacher_auto_gakuseki(client, db):
    """教員のサインアップ: gakuseki_bango自動生成"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "professor",
            "email": "prof@example.com",
            "password": "ProfPass123!",
            "kategori": "教授",
            "gakuseki_bango": None,  # Should be auto-generated
            "faculty": "情報工学科"
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["kategori"] == "教授"
    # Auto-generated gakuseki_bango should start with "staff_"
    assert data["gakuseki_bango"].startswith("staff_")


def test_login_success(client, test_user, db):
    """ログイン成功"""
    response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": test_user.plain_password
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_invalid_username(client, db):
    """ログイン失敗: 存在しないユーザー名"""
    response = client.post(
        "/auth/token",
        data={
            "username": "nonexistent",
            "password": "SomePass123!"
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect" in response.json()["detail"].lower()


def test_login_invalid_password(client, test_user, db):
    """ログイン失敗: 無効なパスワード"""
    response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect" in response.json()["detail"].lower()


def test_get_current_user(authenticated_client, test_user):
    """認証済みユーザー情報取得成功"""
    response = authenticated_client.get("/users/me")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["kategori"] == test_user.kategori.value
    assert str(data["id"]) == str(test_user.id)


def test_get_current_user_unauthorized(client):
    """認証なしでのユーザー情報取得失敗"""
    response = client.get("/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_invalid_token(client):
    """無効なトークンでのユーザー情報取得失敗"""
    client.headers = {
        "Authorization": "Bearer invalid_token_here"
    }

    response = client.get("/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

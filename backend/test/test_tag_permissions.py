"""
Tag permissions tests (タグ権限詳細テスト)

Tests for v3 complex tag assignment permissions:
- 学生: 誰にでもタグを割り当て可能
- 教員: 自分が作成したタグのみ割り当て可能
- タグ削除は作成者のみ
"""
import pytest
from fastapi import status


def test_tag_create_success(authenticated_client, test_user):
    """タグ作成成功"""
    response = authenticated_client.post(
        "/tags",
        json={"name": "Python"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Python"
    assert str(data["creator_id"]) == str(test_user.id)


def test_tag_create_duplicate_name(client, db, test_user):
    """タグ作成失敗: 重複タグ名"""
    # Login and create first tag
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    client.post("/tags", json={"name": "Duplicate"})

    # Try to create same tag name
    response = client.post("/tags", json={"name": "Duplicate"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


def test_student_can_assign_any_tag(client, db, student_user, teacher_user):
    """学生は任意のタグを割り当て可能（v3仕様）"""
    # Login as teacher and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": teacher_user.username, "password": teacher_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    tag_response = client.post("/tags", json={"name": "Teacher Tag"})
    tag_id = tag_response.json()["id"]

    # Login as student
    login_response2 = client.post(
        "/auth/token",
        data={"username": student_user.username, "password": student_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    # Student assigns teacher's tag to themselves
    assign_response = client.post(
        f"/tags/{tag_id}/assign",
        json={"user_id": str(student_user.id)}
    )

    assert assign_response.status_code == status.HTTP_201_CREATED


def test_teacher_can_assign_own_tag(client, db, teacher_user, student_user):
    """教員は自分のタグを割り当て可能（v3仕様）"""
    # Login as teacher and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": teacher_user.username, "password": teacher_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    tag_response = client.post("/tags", json={"name": "Own Tag"})
    tag_id = tag_response.json()["id"]

    # Teacher assigns their own tag to student
    assign_response = client.post(
        f"/tags/{tag_id}/assign",
        json={"user_id": str(student_user.id)}
    )

    assert assign_response.status_code == status.HTTP_201_CREATED


def test_teacher_cannot_assign_others_tag(client, db, teacher_user):
    """教員は他人のタグを割り当て不可（v3仕様）"""
    # Create another teacher
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": "teacher2",
            "email": "teacher2@example.com",
            "password": "Teacher2Pass!",
            "kategori": "教授",
            "gakuseki_bango": None,
            "faculty": "数学科"
        }
    )

    # Login as teacher2 and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": "teacher2", "password": "Teacher2Pass!"}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    tag_response = client.post("/tags", json={"name": "Teacher2 Tag"})
    tag_id = tag_response.json()["id"]

    # Login as original teacher (teacher_user)
    login_response2 = client.post(
        "/auth/token",
        data={"username": teacher_user.username, "password": teacher_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    # Try to assign teacher2's tag (should fail)
    assign_response = client.post(
        f"/tags/{tag_id}/assign",
        json={"user_id": str(teacher_user.id)}
    )

    assert assign_response.status_code == status.HTTP_403_FORBIDDEN


def test_tag_delete_requires_creator(client, db, test_user, other_user):
    """タグ削除は作成者のみ可能"""
    # Login as test_user and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    tag_response = client.post("/tags", json={"name": "Delete Test"})
    tag_id = tag_response.json()["id"]

    # Login as other_user and try to delete
    login_response2 = client.post(
        "/auth/token",
        data={"username": other_user.username, "password": other_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    delete_response = client.delete(f"/tags/{tag_id}")

    assert delete_response.status_code == status.HTTP_403_FORBIDDEN


def test_tag_delete_success_by_creator(client, db, test_user):
    """作成者によるタグ削除成功"""
    # Login as test_user and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    tag_response = client.post("/tags", json={"name": "Creator Delete"})
    tag_id = tag_response.json()["id"]

    # Delete own tag
    delete_response = client.delete(f"/tags/{tag_id}")

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT


def test_tag_list_for_user(client, db, test_user):
    """ユーザーに割り当てられたタグ一覧取得"""
    # Login and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    tag_response = client.post("/tags", json={"name": "User Tag"})
    tag_id = tag_response.json()["id"]

    # Assign to self
    client.post(f"/tags/{tag_id}/assign", json={"user_id": str(test_user.id)})

    # Get tags list
    list_response = client.get("/tags")

    assert list_response.status_code == status.HTTP_200_OK
    tags = list_response.json()
    assert len(tags) >= 1
    assert any(tag["name"] == "User Tag" for tag in tags)


def test_tag_detail_shows_assigned_users(client, db, test_user, other_user):
    """タグ詳細に割り当てられたユーザーが表示される"""
    # Login and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    tag_response = client.post("/tags", json={"name": "Detail Tag"})
    tag_id = tag_response.json()["id"]

    # Assign to other_user
    client.post(f"/tags/{tag_id}/assign", json={"user_id": str(other_user.id)})

    # Get tag detail
    detail_response = client.get(f"/tags/{tag_id}")

    assert detail_response.status_code == status.HTTP_200_OK
    data = detail_response.json()
    assert "assigned_users" in data
    assert len(data["assigned_users"]) >= 1
    assert any(str(user["id"]) == str(other_user.id) for user in data["assigned_users"])


def test_tag_assign_nonexistent_user_fails(client, db, test_user):
    """存在しないユーザーへのタグ割り当て失敗"""
    # Login and create tag
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    tag_response = client.post("/tags", json={"name": "Nonexistent Test"})
    tag_id = tag_response.json()["id"]

    # Try to assign to nonexistent user
    assign_response = client.post(
        f"/tags/{tag_id}/assign",
        json={"user_id": "00000000-0000-0000-0000-000000000000"}
    )

    assert assign_response.status_code == status.HTTP_404_NOT_FOUND

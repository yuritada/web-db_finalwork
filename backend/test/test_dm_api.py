"""
DM (Direct Message) API tests (Phase 4)

Tests for:
- DM sending
- DM history retrieval
- DM pagination
- DM error cases

v3 API Spec Section 5.5: Channels & DM
"""
import pytest
from fastapi import status


def test_send_dm_success(client, test_user, other_user, db):
    """DM送信成功"""
    # Arrange: Login as test_user
    login_response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": test_user.plain_password
        }
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    dm_data = {
        "receiver_id": str(other_user.id),
        "content": "Hello, other user!"
    }

    # Act
    response = client.post("/messages/dm", json=dm_data)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["content"] == "Hello, other user!"
    assert str(data["sender_id"]) == str(test_user.id)
    assert str(data["receiver_id"]) == str(other_user.id)
    assert "created_at" in data


def test_send_dm_to_nonexistent_user(authenticated_client):
    """DM送信: 存在しないユーザー"""
    # Arrange
    dm_data = {
        "receiver_id": "00000000-0000-0000-0000-000000000000",
        "content": "Hello, ghost!"
    }

    # Act
    response = authenticated_client.post("/messages/dm", json=dm_data)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_send_dm_to_self(client, test_user):
    """DM送信: 自分自身へのDM（禁止）"""
    # Arrange: Login
    login_response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": test_user.plain_password
        }
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    dm_data = {
        "receiver_id": str(test_user.id),  # Send to self
        "content": "Talking to myself"
    }

    # Act
    response = client.post("/messages/dm", json=dm_data)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "yourself" in response.json()["detail"].lower()


def test_get_dm_history_success(client, test_user, other_user, test_dm):
    """DM履歴取得成功"""
    # Arrange: Login as test_user
    login_response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": test_user.plain_password
        }
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Act: Get DM history with other_user
    response = client.get(f"/messages/dm/{other_user.id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check message
    message = data[0]
    assert message["content"] == test_dm.content
    assert str(message["sender_id"]) == str(test_user.id)
    assert str(message["receiver_id"]) == str(other_user.id)


def test_get_dm_history_empty(client, test_user, other_user):
    """DM履歴取得: メッセージなし"""
    # Arrange: Login as test_user
    login_response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": test_user.plain_password
        }
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Act: Get DM history with other_user (no messages yet)
    response = client.get(f"/messages/dm/{other_user.id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_dm_history_with_pagination(client, test_user, other_user, db):
    """DM履歴取得: ページネーション"""
    from app.models.message import Message

    # Arrange: Login as test_user
    login_response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": test_user.plain_password
        }
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Create 10 DM messages
    for i in range(10):
        msg = Message(
            content=f"DM {i}",
            sender_id=test_user.id,
            receiver_id=other_user.id
        )
        db.add(msg)
    db.commit()

    # Act: Get first 5 messages
    response = client.get(f"/messages/dm/{other_user.id}?limit=5&offset=0")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 5

    # Act: Get next 5 messages
    response2 = client.get(f"/messages/dm/{other_user.id}?limit=5&offset=5")

    # Assert
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    assert len(data2) == 5

    # Verify no overlap
    message_ids_1 = [m["id"] for m in data]
    message_ids_2 = [m["id"] for m in data2]
    assert len(set(message_ids_1) & set(message_ids_2)) == 0

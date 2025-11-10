"""
Channel API tests (Phase 4)

Tests for:
- Channel CRUD operations
- Channel message posting
- Channel message history retrieval
- Pagination

v3 API Spec Section 5.5: Channels & DM
"""
import pytest
from fastapi import status


# ===== Helper function =====

def get_auth_headers(client, test_user):
    """Get authentication headers for a user"""
    login_response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": test_user.plain_password
        }
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ===== Channel CRUD Tests =====

def test_create_channel_success(client, test_user, db):
    """チャンネル作成成功"""
    # Arrange
    headers = get_auth_headers(client, test_user)
    channel_data = {
        "name": "New Channel",
        "description": "A brand new channel",
        "is_private": False
    }

    # Act
    response = client.post("/channels", json=channel_data, headers=headers)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Channel"
    assert data["description"] == "A brand new channel"
    assert data["is_private"] is False
    assert "id" in data


def test_create_channel_duplicate_name(client, test_user, test_channel, db):
    """チャンネル作成: 重複名エラー"""
    # Arrange
    headers = get_auth_headers(client, test_user)
    channel_data = {
        "name": test_channel.name,  # Duplicate name
        "description": "Duplicate channel",
        "is_private": False
    }

    # Act
    response = client.post("/channels", json=channel_data, headers=headers)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


def test_get_channels_list(client, test_user, test_channel, private_channel, db):
    """チャンネル一覧取得"""
    # Arrange
    headers = get_auth_headers(client, test_user)

    # Act
    response = client.get("/channels", headers=headers)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # Check that both channels are in the list
    channel_names = [ch["name"] for ch in data]
    assert test_channel.name in channel_names
    assert private_channel.name in channel_names


def test_get_channels_empty(client, test_user, db):
    """チャンネル一覧取得: チャンネルなし"""
    # Arrange
    headers = get_auth_headers(client, test_user)

    # Act
    response = client.get("/channels", headers=headers)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_create_private_channel(client, test_user, db):
    """プライベートチャンネル作成"""
    # Arrange
    headers = get_auth_headers(client, test_user)
    channel_data = {
        "name": "Secret Channel",
        "description": "Private channel for testing",
        "is_private": True
    }

    # Act
    response = client.post("/channels", json=channel_data, headers=headers)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Secret Channel"
    assert data["is_private"] is True


def test_create_channel_unauthorized(client):
    """チャンネル作成: 未認証エラー"""
    # Arrange
    channel_data = {
        "name": "Unauthorized Channel",
        "description": "Should fail",
        "is_private": False
    }

    # Act
    response = client.post("/channels", json=channel_data)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ===== Channel Messaging Tests =====

def test_post_channel_message_success(client, test_user, test_channel, db):
    """チャンネルメッセージ投稿成功"""
    # Arrange
    headers = get_auth_headers(client, test_user)
    message_data = {
        "content": "Hello, channel!"
    }

    # Act
    response = client.post(
        f"/channels/{test_channel.id}/messages",
        json=message_data,
        headers=headers
    )

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["content"] == "Hello, channel!"
    assert data["sender_username"] == test_user.username
    assert data["channel_id"] == test_channel.id
    assert str(data["sender_id"]) == str(test_user.id)
    assert "created_at" in data


def test_post_channel_message_nonexistent_channel(client, test_user, db):
    """チャンネルメッセージ投稿: 存在しないチャンネル"""
    # Arrange
    headers = get_auth_headers(client, test_user)
    message_data = {
        "content": "Hello, nobody!"
    }

    # Act
    response = client.post(
        "/channels/99999/messages",
        json=message_data,
        headers=headers
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_channel_messages_success(client, test_user, test_channel, test_channel_message, db):
    """チャンネルメッセージ履歴取得"""
    # Arrange
    headers = get_auth_headers(client, test_user)

    # Act
    response = client.get(f"/channels/{test_channel.id}/messages", headers=headers)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check message content
    message = data[0]
    assert message["content"] == test_channel_message.content
    assert "sender_username" in message
    assert message["channel_id"] == test_channel.id


def test_get_channel_messages_empty(client, test_user, test_channel, db):
    """チャンネルメッセージ履歴取得: メッセージなし"""
    # Arrange
    headers = get_auth_headers(client, test_user)

    # Act
    response = client.get(f"/channels/{test_channel.id}/messages", headers=headers)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_channel_messages_with_pagination(client, test_user, test_channel, db):
    """チャンネルメッセージ取得: ページネーション"""
    from app.models.message import Message

    # Arrange: Create 10 messages
    headers = get_auth_headers(client, test_user)
    for i in range(10):
        msg = Message(
            content=f"Message {i}",
            sender_id=test_user.id,
            channel_id=test_channel.id
        )
        db.add(msg)
    db.commit()

    # Act: Get first 5 messages
    response = client.get(
        f"/channels/{test_channel.id}/messages?limit=5&offset=0",
        headers=headers
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 5

    # Act: Get next 5 messages
    response2 = client.get(
        f"/channels/{test_channel.id}/messages?limit=5&offset=5",
        headers=headers
    )

    # Assert
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    assert len(data2) == 5

    # Verify no overlap
    message_ids_1 = [m["id"] for m in data]
    message_ids_2 = [m["id"] for m in data2]
    assert len(set(message_ids_1) & set(message_ids_2)) == 0

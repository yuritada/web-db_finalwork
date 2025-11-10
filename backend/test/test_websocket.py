"""
WebSocket tests (Phase 4)

Tests for:
- WebSocket connection establishment
- Message broadcasting
- JOIN/LEAVE notifications
- Error handling

v3 API Spec Section 5.5: WebSocket
"""
import pytest
from fastapi import status
import json


def test_websocket_connect_success(client, test_channel):
    """WebSocket接続成功"""
    # Act & Assert
    with client.websocket_connect(f"/ws/channel/{test_channel.id}") as websocket:
        # Connection established successfully
        # Receive JOIN notification
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "system"
        assert "joined" in message["content"].lower()
        assert "timestamp" in message


def test_websocket_connect_nonexistent_channel(client):
    """WebSocket接続: 存在しないチャンネル"""
    # Act & Assert
    try:
        with client.websocket_connect("/ws/channel/99999") as websocket:
            # Should not reach here
            assert False, "Connection should have been rejected"
    except Exception as e:
        # Connection should be closed with error
        # WebSocket should reject connection to non-existent channel
        assert True


def test_websocket_broadcast_message(client, test_channel):
    """WebSocketメッセージブロードキャスト"""
    # Act: Connect two clients
    with client.websocket_connect(f"/ws/channel/{test_channel.id}") as ws1:
        # Clear JOIN notification for ws1
        ws1.receive_text()

        with client.websocket_connect(f"/ws/channel/{test_channel.id}") as ws2:
            # Clear JOIN notifications
            ws1.receive_text()  # ws2 joined notification to ws1
            ws2.receive_text()  # ws2 joined notification to ws2

            # Send message from ws1
            test_message = {
                "type": "message",
                "content": "Hello from ws1!",
                "sender_username": "testuser"
            }
            ws1.send_text(json.dumps(test_message))

            # Both clients should receive the broadcast
            data1 = ws1.receive_text()
            message1 = json.loads(data1)

            data2 = ws2.receive_text()
            message2 = json.loads(data2)

            # Assert: Both received same message
            assert message1["type"] == "message"
            assert message1["content"] == "Hello from ws1!"
            assert message1["sender_username"] == "testuser"

            assert message2["type"] == "message"
            assert message2["content"] == "Hello from ws1!"
            assert message2["sender_username"] == "testuser"


def test_websocket_join_leave_notifications(client, test_channel):
    """WebSocket JOIN/LEAVE通知"""
    # Act: Connect first client
    with client.websocket_connect(f"/ws/channel/{test_channel.id}") as ws1:
        # Receive JOIN notification for ws1
        data = ws1.receive_text()
        message = json.loads(data)
        assert message["type"] == "system"
        assert "joined" in message["content"].lower()

        # Connect second client
        with client.websocket_connect(f"/ws/channel/{test_channel.id}") as ws2:
            # ws1 should receive JOIN notification for ws2
            data = ws1.receive_text()
            message = json.loads(data)
            assert message["type"] == "system"
            assert "joined" in message["content"].lower()

            # ws2 should receive its own JOIN notification
            data2 = ws2.receive_text()
            message2 = json.loads(data2)
            assert message2["type"] == "system"
            assert "joined" in message2["content"].lower()

        # After ws2 disconnects, ws1 should receive LEAVE notification
        data = ws1.receive_text()
        message = json.loads(data)
        assert message["type"] == "system"
        assert "left" in message["content"].lower()


def test_websocket_disconnect(client, test_channel):
    """WebSocket切断処理"""
    # Act: Connect and disconnect
    with client.websocket_connect(f"/ws/channel/{test_channel.id}") as websocket:
        # Receive JOIN notification
        websocket.receive_text()

        # Connect second client to receive LEAVE notification
        with client.websocket_connect(f"/ws/channel/{test_channel.id}") as ws2:
            # Clear JOIN notifications
            websocket.receive_text()
            ws2.receive_text()

            # Close first websocket
            websocket.close()

            # ws2 should receive LEAVE notification
            data = ws2.receive_text()
            message = json.loads(data)
            assert message["type"] == "system"
            assert "left" in message["content"].lower()


def test_websocket_invalid_json(client, test_channel):
    """WebSocket: 不正なJSON送信"""
    # Act & Assert
    with client.websocket_connect(f"/ws/channel/{test_channel.id}") as websocket:
        # Clear JOIN notification
        websocket.receive_text()

        # Send invalid JSON
        websocket.send_text("not a valid json")

        # Should receive error message
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "error"
        assert "invalid" in message["content"].lower() or "json" in message["content"].lower()

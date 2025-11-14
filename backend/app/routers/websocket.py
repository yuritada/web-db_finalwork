"""
WebSocket endpoints for real-time messaging
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.orm import Session
import logging
import uuid
import json

from app.db.connect import get_session
from app.websocket import manager
from app.auth.dependencies import get_current_user_ws
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/channels/{channel_id}")
async def websocket_channel_endpoint(
    websocket: WebSocket,
    channel_id: int,
    db: Session = Depends(get_session)
):
    """
    チャンネル用WebSocketエンドポイント

    接続時にトークンで認証を行い、チャンネルに参加
    メッセージを受信したらチャンネルの全員にブロードキャスト

    Query Parameters:
        token: JWTアクセストークン
    """
    # トークンから現在のユーザーを取得
    try:
        # クエリパラメータからトークンを取得
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # トークンを検証してユーザーを取得
        current_user = await get_current_user_ws(token, db)
        if not current_user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # チャンネルに接続
    await manager.connect_to_channel(websocket, channel_id, current_user.id)

    try:
        # 接続成功メッセージを送信
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "channel_id": channel_id,
            "user_id": str(current_user.id),
            "username": current_user.username
        })

        # メッセージ受信ループ
        while True:
            # クライアントからメッセージを受信
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)

                # メッセージタイプに応じて処理
                if message_data.get("type") == "ping":
                    # Ping-Pong（接続維持）
                    await websocket.send_json({"type": "pong"})

                elif message_data.get("type") == "message":
                    # 新しいメッセージ - チャンネルの全員にブロードキャスト
                    # 注意: 実際のメッセージ保存はHTTP APIで行う
                    # WebSocketはリアルタイム通知のみ
                    broadcast_message = {
                        "type": "new_message",
                        "channel_id": channel_id,
                        "message": message_data.get("message"),
                        "sender_id": str(current_user.id),
                        "sender_username": current_user.username
                    }
                    await manager.broadcast_to_channel(channel_id, broadcast_message)

                else:
                    logger.warning(f"Unknown message type: {message_data.get('type')}")

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })

    except WebSocketDisconnect:
        manager.disconnect_from_channel(channel_id, current_user.id)
        logger.info(
            f"User {current_user.username} disconnected from channel {channel_id}"
        )

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect_from_channel(channel_id, current_user.id)


@router.websocket("/ws/dm/{partner_id}")
async def websocket_dm_endpoint(
    websocket: WebSocket,
    partner_id: str,
    db: Session = Depends(get_session)
):
    """
    DM用WebSocketエンドポイント

    接続時にトークンで認証を行い、DMルームに参加
    メッセージを受信したら相手にブロードキャスト

    Query Parameters:
        token: JWTアクセストークン
    """
    # トークンから現在のユーザーを取得
    try:
        # クエリパラメータからトークンを取得
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # トークンを検証してユーザーを取得
        current_user = await get_current_user_ws(token, db)
        if not current_user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # partner_idをUUIDに変換
        try:
            partner_uuid = uuid.UUID(partner_id)
        except ValueError:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # DMルームに接続
    await manager.connect_to_dm(websocket, current_user.id, partner_uuid)

    try:
        # 接続成功メッセージを送信
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "partner_id": partner_id,
            "user_id": str(current_user.id),
            "username": current_user.username
        })

        # メッセージ受信ループ
        while True:
            # クライアントからメッセージを受信
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)

                # メッセージタイプに応じて処理
                if message_data.get("type") == "ping":
                    # Ping-Pong（接続維持）
                    await websocket.send_json({"type": "pong"})

                elif message_data.get("type") == "message":
                    # 新しいメッセージ - DMルームの全員にブロードキャスト
                    # 注意: 実際のメッセージ保存はHTTP APIで行う
                    # WebSocketはリアルタイム通知のみ
                    broadcast_message = {
                        "type": "new_message",
                        "partner_id": partner_id,
                        "message": message_data.get("message"),
                        "sender_id": str(current_user.id),
                        "sender_username": current_user.username
                    }
                    await manager.broadcast_to_dm(
                        current_user.id,
                        partner_uuid,
                        broadcast_message
                    )

                else:
                    logger.warning(f"Unknown message type: {message_data.get('type')}")

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })

    except WebSocketDisconnect:
        manager.disconnect_from_dm(current_user.id, partner_uuid)
        logger.info(
            f"User {current_user.username} disconnected from DM with {partner_id}"
        )

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect_from_dm(current_user.id, partner_uuid)

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
            logger.warning("WebSocket connection rejected: no token provided")
            await websocket.close(code=4001, reason="No authentication token provided")
            return

        # トークンを検証してユーザーを取得
        current_user = await get_current_user_ws(token, db)
        if not current_user:
            logger.warning("WebSocket connection rejected: invalid token")
            await websocket.close(code=4001, reason="Invalid or expired token")
            return

    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=4000, reason="Authentication error")
        return

    # チャンネルに接続
    logger.info(f"Connecting user {current_user.username} to channel {channel_id}")
    await manager.connect_to_channel(websocket, channel_id, current_user.id)
    logger.info(f"User {current_user.username} connected to channel {channel_id} successfully")

    try:
        # 接続成功メッセージを送信
        connection_message = {
            "type": "connection",
            "status": "connected",
            "channel_id": channel_id,
            "user_id": str(current_user.id),
            "username": current_user.username
        }
        logger.info(f"Sending connection message: {connection_message}")
        await websocket.send_json(connection_message)
        logger.info("Connection message sent successfully")

        # メッセージ受信ループ
        logger.info("Entering message receive loop")
        while True:
            # クライアントからメッセージを受信
            logger.debug("Waiting for message from client...")
            data = await websocket.receive_text()
            logger.info(f"Received data: {data}")

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

    except WebSocketDisconnect as e:
        logger.info(f"WebSocketDisconnect: User {current_user.username} disconnected from channel {channel_id}, code: {e.code if hasattr(e, 'code') else 'unknown'}")
        manager.disconnect_from_channel(channel_id, current_user.id)

    except Exception as e:
        logger.error(f"WebSocket unexpected error: {type(e).__name__}: {e}", exc_info=True)
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
            logger.warning("WebSocket connection rejected: no token provided")
            await websocket.close(code=4001, reason="No authentication token provided")
            return

        # トークンを検証してユーザーを取得
        current_user = await get_current_user_ws(token, db)
        if not current_user:
            logger.warning("WebSocket connection rejected: invalid token")
            await websocket.close(code=4001, reason="Invalid or expired token")
            return

        # partner_idをUUIDに変換
        try:
            partner_uuid = uuid.UUID(partner_id)
        except ValueError as e:
            logger.warning(f"WebSocket connection rejected: invalid partner_id {partner_id}")
            await websocket.close(code=4000, reason="Invalid partner ID format")
            return

    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=4000, reason="Authentication error")
        return

    # DMルームに接続
    print(f"[DEBUG DM] Connecting user {current_user.username} to DM with {partner_id}", flush=True)
    logger.info(f"Connecting user {current_user.username} to DM with {partner_id}")

    try:
        await manager.connect_to_dm(websocket, current_user.id, partner_uuid)
        print(f"[DEBUG DM] connect_to_dm completed", flush=True)
    except Exception as e:
        print(f"[DEBUG DM] connect_to_dm failed: {e}", flush=True)
        logger.error(f"Failed to connect to DM: {e}", exc_info=True)
        return

    logger.info(f"User {current_user.username} connected to DM successfully")

    try:
        # 接続成功メッセージを送信
        print(f"[DEBUG DM] Creating connection message", flush=True)
        connection_message = {
            "type": "connection",
            "status": "connected",
            "partner_id": partner_id,
            "user_id": str(current_user.id),
            "username": current_user.username
        }
        print(f"[DEBUG DM] Sending connection message", flush=True)
        await websocket.send_json(connection_message)
        print(f"[DEBUG DM] Connection message sent successfully", flush=True)
        logger.info(f"Connection established for {current_user.username}")

        # メッセージ受信ループ
        while True:
            # クライアントからメッセージを受信
            data = await websocket.receive_text()
            logger.debug(f"Received data from {current_user.username}: {data[:100]}...")

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

    except WebSocketDisconnect as e:
        logger.info(f"User {current_user.username} disconnected from DM with {partner_id}, code: {e.code if hasattr(e, 'code') else 'unknown'}")
        manager.disconnect_from_dm(current_user.id, partner_uuid)

    except Exception as e:
        logger.error(f"WebSocket error for {current_user.username}: {type(e).__name__}: {e}", exc_info=True)
        manager.disconnect_from_dm(current_user.id, partner_uuid)

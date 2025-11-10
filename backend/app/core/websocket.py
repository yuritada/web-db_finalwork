"""
WebSocket接続管理
リアルタイムチャンネル通信のための接続プール管理

v3仕様書 セクション5.5 WebSocket準拠
"""
from fastapi import WebSocket
from typing import Dict, List
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket接続管理クラス

    チャンネルごとに接続を管理し、ブロードキャスト機能を提供

    **主な機能:**
        - チャンネル単位での接続管理
        - メッセージのブロードキャスト
        - 個別メッセージ送信
        - 接続/切断の自動管理

    **データ構造:**
        active_connections: {channel_id: [WebSocket, WebSocket, ...]}
    """

    def __init__(self):
        """ConnectionManagerを初期化する"""
        # {channel_id: [WebSocket, WebSocket, ...]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel_id: int):
        """
        WebSocket接続を受け入れ、チャンネルに登録する

        Args:
            websocket: WebSocketインスタンス
            channel_id: チャンネルID

        Raises:
            Exception: WebSocket接続受け入れに失敗した場合
        """
        await websocket.accept()

        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []

        self.active_connections[channel_id].append(websocket)

        logger.info(
            f"WebSocket connected: channel_id={channel_id}, "
            f"total_connections={len(self.active_connections[channel_id])}"
        )

    def disconnect(self, websocket: WebSocket, channel_id: int):
        """
        WebSocket接続を切断し、チャンネルから削除する

        Args:
            websocket: WebSocketインスタンス
            channel_id: チャンネルID
        """
        if channel_id in self.active_connections:
            try:
                self.active_connections[channel_id].remove(websocket)
                logger.info(
                    f"WebSocket disconnected: channel_id={channel_id}, "
                    f"remaining_connections={len(self.active_connections[channel_id])}"
                )
            except ValueError:
                # WebSocketが既に削除されている場合
                logger.warning(
                    f"Attempted to remove non-existent WebSocket from channel {channel_id}"
                )

            # チャンネルに接続がなくなったら削除
            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]
                logger.info(f"Channel {channel_id} removed (no active connections)")

    async def broadcast(self, channel_id: int, message: dict):
        """
        チャンネルの全接続にメッセージをブロードキャストする

        Args:
            channel_id: チャンネルID
            message: 送信するメッセージ（辞書形式、JSON変換される）

        Note:
            送信に失敗した接続は自動的に削除されます
        """
        if channel_id not in self.active_connections:
            logger.debug(f"No active connections for channel {channel_id}")
            return

        # JSON文字列に変換（datetime等も文字列に変換）
        message_json = json.dumps(message, default=str)

        # 送信失敗した接続を記録
        disconnected = []

        # 全接続に送信
        for connection in self.active_connections[channel_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(
                    f"Failed to send message to WebSocket: {e}, "
                    f"channel_id={channel_id}"
                )
                disconnected.append(connection)

        # 送信失敗した接続を削除
        for connection in disconnected:
            self.disconnect(connection, channel_id)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        特定のWebSocket接続にメッセージを送信する

        Args:
            message: 送信するメッセージ（辞書形式）
            websocket: 送信先WebSocketインスタンス

        Raises:
            Exception: メッセージ送信に失敗した場合
        """
        message_json = json.dumps(message, default=str)
        await websocket.send_text(message_json)

    def get_connection_count(self, channel_id: int) -> int:
        """
        チャンネルの接続数を取得する

        Args:
            channel_id: チャンネルID

        Returns:
            int: 接続数
        """
        if channel_id not in self.active_connections:
            return 0
        return len(self.active_connections[channel_id])

    def get_total_connections(self) -> int:
        """
        全チャンネルの総接続数を取得する

        Returns:
            int: 総接続数
        """
        return sum(len(connections) for connections in self.active_connections.values())

    def get_active_channels(self) -> List[int]:
        """
        接続が存在するチャンネルIDのリストを取得する

        Returns:
            List[int]: アクティブなチャンネルIDのリスト
        """
        return list(self.active_connections.keys())


# グローバルインスタンス（アプリケーション全体で共有）
manager = ConnectionManager()

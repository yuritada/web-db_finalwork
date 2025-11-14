"""
WebSocket Connection Manager
リアルタイムメッセージング用のWebSocket接続を管理
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import logging
import uuid

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket接続を管理するクラス

    チャンネルとDMの両方に対応し、接続されたクライアントに
    リアルタイムでメッセージをブロードキャストする
    """

    def __init__(self):
        # チャンネルごとの接続リスト: {channel_id: {user_id: WebSocket}}
        self.channel_connections: Dict[int, Dict[str, WebSocket]] = {}

        # DMルームごとの接続リスト: {room_key: {user_id: WebSocket}}
        # room_keyは2つのuser_idをソートして結合したもの
        self.dm_connections: Dict[str, Dict[str, WebSocket]] = {}

        # ユーザーごとのアクティブ接続数（デバッグ用）
        self.user_connection_count: Dict[str, int] = {}

    def _get_dm_room_key(self, user_id1: str, user_id2: str) -> str:
        """
        2人のユーザーIDからDMルームキーを生成
        順序に関わらず同じキーを返す
        """
        ids = sorted([str(user_id1), str(user_id2)])
        return f"dm:{ids[0]}:{ids[1]}"

    async def connect_to_channel(
        self,
        websocket: WebSocket,
        channel_id: int,
        user_id: uuid.UUID
    ):
        """
        チャンネルに接続

        Args:
            websocket: WebSocketインスタンス
            channel_id: チャンネルID
            user_id: ユーザーID
        """
        await websocket.accept()

        user_id_str = str(user_id)

        # チャンネルの接続辞書を初期化
        if channel_id not in self.channel_connections:
            self.channel_connections[channel_id] = {}

        # 既存の接続があれば切断
        if user_id_str in self.channel_connections[channel_id]:
            old_ws = self.channel_connections[channel_id][user_id_str]
            try:
                await old_ws.close()
            except Exception as e:
                logger.warning(f"Error closing old connection: {e}")

        # 新しい接続を追加
        self.channel_connections[channel_id][user_id_str] = websocket

        # 接続数をカウント
        self.user_connection_count[user_id_str] = \
            self.user_connection_count.get(user_id_str, 0) + 1

        logger.info(
            f"User {user_id_str} connected to channel {channel_id}. "
            f"Total connections in channel: {len(self.channel_connections[channel_id])}"
        )

    async def connect_to_dm(
        self,
        websocket: WebSocket,
        user_id1: uuid.UUID,
        user_id2: uuid.UUID
    ):
        """
        DMルームに接続

        Args:
            websocket: WebSocketインスタンス
            user_id1: 接続するユーザーID
            user_id2: 相手のユーザーID
        """
        await websocket.accept()

        room_key = self._get_dm_room_key(user_id1, user_id2)
        user_id_str = str(user_id1)

        # DMルームの接続辞書を初期化
        if room_key not in self.dm_connections:
            self.dm_connections[room_key] = {}

        # 既存の接続があれば切断
        if user_id_str in self.dm_connections[room_key]:
            old_ws = self.dm_connections[room_key][user_id_str]
            try:
                await old_ws.close()
            except Exception as e:
                logger.warning(f"Error closing old connection: {e}")

        # 新しい接続を追加
        self.dm_connections[room_key][user_id_str] = websocket

        # 接続数をカウント
        self.user_connection_count[user_id_str] = \
            self.user_connection_count.get(user_id_str, 0) + 1

        logger.info(
            f"User {user_id_str} connected to DM room {room_key}. "
            f"Total connections in room: {len(self.dm_connections[room_key])}"
        )

    def disconnect_from_channel(self, channel_id: int, user_id: uuid.UUID):
        """
        チャンネルから切断

        Args:
            channel_id: チャンネルID
            user_id: ユーザーID
        """
        user_id_str = str(user_id)

        if channel_id in self.channel_connections:
            if user_id_str in self.channel_connections[channel_id]:
                del self.channel_connections[channel_id][user_id_str]

                # 接続数を減らす
                if user_id_str in self.user_connection_count:
                    self.user_connection_count[user_id_str] -= 1
                    if self.user_connection_count[user_id_str] <= 0:
                        del self.user_connection_count[user_id_str]

                logger.info(f"User {user_id_str} disconnected from channel {channel_id}")

                # チャンネルに接続がなくなったら削除
                if not self.channel_connections[channel_id]:
                    del self.channel_connections[channel_id]

    def disconnect_from_dm(self, user_id1: uuid.UUID, user_id2: uuid.UUID):
        """
        DMルームから切断

        Args:
            user_id1: 切断するユーザーID
            user_id2: 相手のユーザーID
        """
        room_key = self._get_dm_room_key(user_id1, user_id2)
        user_id_str = str(user_id1)

        if room_key in self.dm_connections:
            if user_id_str in self.dm_connections[room_key]:
                del self.dm_connections[room_key][user_id_str]

                # 接続数を減らす
                if user_id_str in self.user_connection_count:
                    self.user_connection_count[user_id_str] -= 1
                    if self.user_connection_count[user_id_str] <= 0:
                        del self.user_connection_count[user_id_str]

                logger.info(f"User {user_id_str} disconnected from DM room {room_key}")

                # ルームに接続がなくなったら削除
                if not self.dm_connections[room_key]:
                    del self.dm_connections[room_key]

    async def broadcast_to_channel(self, channel_id: int, message: dict):
        """
        チャンネルの全接続にメッセージをブロードキャスト

        Args:
            channel_id: チャンネルID
            message: 送信するメッセージ（辞書形式）
        """
        if channel_id not in self.channel_connections:
            logger.warning(f"No connections found for channel {channel_id}")
            return

        # 切断された接続を記録
        disconnected = []

        for user_id_str, websocket in self.channel_connections[channel_id].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to user {user_id_str}: {e}")
                disconnected.append(user_id_str)

        # 切断された接続を削除
        for user_id_str in disconnected:
            try:
                user_id = uuid.UUID(user_id_str)
                self.disconnect_from_channel(channel_id, user_id)
            except Exception as e:
                logger.error(f"Error disconnecting user {user_id_str}: {e}")

        logger.info(
            f"Broadcasted message to channel {channel_id}. "
            f"Sent to {len(self.channel_connections[channel_id])} users"
        )

    async def broadcast_to_dm(self, user_id1: uuid.UUID, user_id2: uuid.UUID, message: dict):
        """
        DMルームの全接続にメッセージをブロードキャスト

        Args:
            user_id1: 送信者のユーザーID
            user_id2: 受信者のユーザーID
            message: 送信するメッセージ（辞書形式）
        """
        room_key = self._get_dm_room_key(user_id1, user_id2)

        if room_key not in self.dm_connections:
            logger.warning(f"No connections found for DM room {room_key}")
            return

        # 切断された接続を記録
        disconnected = []

        for user_id_str, websocket in self.dm_connections[room_key].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to user {user_id_str}: {e}")
                disconnected.append(user_id_str)

        # 切断された接続を削除
        for user_id_str in disconnected:
            # どちらのユーザーかを判定
            if user_id_str == str(user_id1):
                self.disconnect_from_dm(user_id1, user_id2)
            else:
                self.disconnect_from_dm(uuid.UUID(user_id_str), user_id1)

        logger.info(
            f"Broadcasted message to DM room {room_key}. "
            f"Sent to {len(self.dm_connections[room_key])} users"
        )

    def get_channel_user_count(self, channel_id: int) -> int:
        """チャンネルの接続ユーザー数を取得"""
        if channel_id in self.channel_connections:
            return len(self.channel_connections[channel_id])
        return 0

    def get_dm_user_count(self, user_id1: uuid.UUID, user_id2: uuid.UUID) -> int:
        """DMルームの接続ユーザー数を取得"""
        room_key = self._get_dm_room_key(user_id1, user_id2)
        if room_key in self.dm_connections:
            return len(self.dm_connections[room_key])
        return 0


# グローバルなConnectionManagerインスタンス
manager = ConnectionManager()

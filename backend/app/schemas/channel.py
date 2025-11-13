"""
チャンネル/DM API スキーマ定義
v3仕様書 セクション5.5 準拠
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from app.schemas.user import UserInfo


# ===== チャンネル関連 =====

class ChannelCreate(BaseModel):
    """チャンネル作成リクエスト

    v3仕様書: POST /channels
    """
    name: str = Field(..., min_length=1, max_length=100, description="チャンネル名")
    description: Optional[str] = Field(None, max_length=500, description="チャンネル説明")
    is_private: bool = Field(default=False, description="プライベートチャンネルか")


class ChannelPublic(BaseModel):
    """チャンネル公開情報

    v3仕様書: GET /channels レスポンス
    """
    id: int
    name: str
    description: Optional[str]
    is_private: bool

    model_config = {"from_attributes": True}


class ChannelDetail(ChannelPublic):
    """チャンネル詳細情報

    v3仕様書: GET /channels/{channel_id} レスポンス
    フロントエンドが期待する型に対応
    """
    created_at: datetime = Field(..., description="チャンネル作成日時")
    member_count: int = Field(default=0, description="メンバー数")
    members: List[UserInfo] = Field(default=[], description="メンバーリスト（Phase 5で実装予定）")

    model_config = {"from_attributes": True}


# ===== メッセージ関連 =====

class MessageCreate(BaseModel):
    """メッセージ作成リクエスト（チャンネル用）

    v3仕様書: POST /channels/{channel_id}/messages
    """
    content: str = Field(..., min_length=1, description="メッセージ内容")


class DMCreate(BaseModel):
    """DM作成リクエスト

    v3仕様書: POST /messages/dm
    """
    receiver_id: uuid.UUID = Field(..., description="受信者のユーザーID")
    content: str = Field(..., min_length=1, description="メッセージ内容")


class MessagePublic(BaseModel):
    """メッセージ公開情報（基本）

    v3仕様書: メッセージレスポンス
    """
    id: int
    content: str
    sender_id: uuid.UUID
    channel_id: Optional[int]
    receiver_id: Optional[uuid.UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageWithSender(BaseModel):
    """送信者情報付きメッセージ

    v3仕様書: GET /channels/{id}/messages レスポンス
    JOINしてsender.usernameを含む
    """
    id: int
    content: str
    sender_id: uuid.UUID
    sender_username: str  # JOIN必須フィールド
    channel_id: Optional[int]
    receiver_id: Optional[uuid.UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class DMConversation(BaseModel):
    """DM会話情報

    v3仕様書: GET /messages/dm レスポンス
    特定ユーザーとのDM一覧表示用
    """
    user_id: uuid.UUID
    username: str
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = Field(default=0, description="未読メッセージ数（将来実装）")


# ===== WebSocket関連 =====

class WebSocketMessage(BaseModel):
    """WebSocket送信メッセージフォーマット

    クライアント→サーバー、サーバー→クライアント両方で使用
    """
    type: str = Field(
        ...,
        description="メッセージタイプ (message/system/error/join/leave)"
    )
    content: Optional[str] = Field(None, description="メッセージ内容")
    sender_id: Optional[uuid.UUID] = Field(None, description="送信者ID")
    sender_username: Optional[str] = Field(None, description="送信者ユーザー名")
    timestamp: Optional[datetime] = Field(None, description="タイムスタンプ")

    model_config = {"from_attributes": True}


class WebSocketConnectionRequest(BaseModel):
    """WebSocket接続リクエスト（認証用）

    クエリパラメータまたは初回メッセージで送信
    """
    token: str = Field(..., description="JWT access token")


# ===== ページネーション対応（将来の拡張）=====

class PaginatedMessages(BaseModel):
    """ページネーション付きメッセージレスポンス（将来実装）"""
    messages: List[MessageWithSender]
    total: int
    limit: int
    offset: int
    has_more: bool

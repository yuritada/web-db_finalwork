"""
チャンネル API エンドポイント (v3)
v3仕様書 セクション5.5 準拠
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.connect import get_session
from app.db.create import create_channel, create_channel_message, add_channel_member
from app.db.read import (
    get_all_channels,
    get_channel_by_id,
    get_channel_messages_with_sender,
    get_user_by_id,
    get_channel_members
)
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.channel import (
    ChannelCreate,
    ChannelPublic,
    ChannelDetail,
    MessageCreate,
    MessageWithSender
)
from pydantic import BaseModel


# リクエストスキーマ
class MemberAddRequest(BaseModel):
    user_id: str


router = APIRouter(prefix="/channels", tags=["Channels"])


# ===== チャンネル管理 =====

@router.post("", response_model=ChannelPublic, status_code=status.HTTP_201_CREATED)
async def create_new_channel(
    channel_data: ChannelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    チャンネルを作成する

    v3仕様書: POST /channels

    **認証**: 必須

    **権限**: 全ユーザーがチャンネル作成可能

    **Args:**
        channel_data: チャンネル作成データ
            - name: チャンネル名（1-100文字、ユニーク）
            - description: チャンネル説明（任意、最大500文字）
            - is_private: プライベートチャンネルか（デフォルト: false）
        current_user: 認証済みユーザー
        db: データベースセッション

    **Returns:**
        ChannelPublic: 作成されたチャンネル情報

    **Raises:**
        400: チャンネル名が既に存在する場合
        401: 未認証の場合
    """
    try:
        channel = create_channel(db, channel_data)
        # チャンネル作成者を自動的にメンバーとして追加
        add_channel_member(db, channel.id, current_user.id)
        return channel
    except Exception as e:
        # IntegrityError (重複チャンネル名など)
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Channel name '{channel_data.name}' already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create channel: {str(e)}"
        )


@router.get("", response_model=List[ChannelPublic])
async def get_channels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    チャンネル一覧を取得する

    v3仕様書: GET /channels

    **認証**: 必須

    **権限**: 全ユーザーが全チャンネル閲覧可能

    Note: v3仕様書では権限管理なし。is_privateによる制限は将来実装予定。

    **Args:**
        current_user: 認証済みユーザー
        db: データベースセッション

    **Returns:**
        List[ChannelPublic]: チャンネル一覧（ID順）

    **Raises:**
        401: 未認証の場合
    """
    channels = get_all_channels(db)
    return channels


@router.get("/{channel_id}", response_model=ChannelDetail)
async def get_channel_details(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    チャンネル詳細を取得する

    v3仕様書: GET /channels/{channel_id}

    **認証**: 必須

    **権限**: 全ユーザーが全チャンネル閲覧可能

    **Args:**
        channel_id: チャンネルID
        current_user: 認証済みユーザー
        db: データベースセッション

    **Returns:**
        ChannelDetail: チャンネル詳細情報
            - id: チャンネルID
            - name: チャンネル名
            - description: チャンネル説明
            - is_private: プライベートチャンネルか
            - created_at: 作成日時
            - member_count: メンバー数（現在は0）
            - members: メンバーリスト（現在は空配列）

    **Raises:**
        404: チャンネルが存在しない場合
        401: 未認証の場合
    """
    channel = get_channel_by_id(db, channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel with id {channel_id} not found"
        )

    # メンバー情報を取得
    members = get_channel_members(db, channel_id)

    # ChannelDetail型で返す
    return ChannelDetail(
        id=channel.id,
        name=channel.name,
        description=channel.description,
        is_private=channel.is_private,
        created_at=channel.created_at,
        member_count=len(members),
        members=members
    )


# ===== チャンネルメッセージ =====

@router.post("/{channel_id}/messages", response_model=MessageWithSender, status_code=status.HTTP_201_CREATED)
async def post_channel_message(
    channel_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    チャンネルにメッセージを投稿する

    v3仕様書: POST /channels/{channel_id}/messages

    **認証**: 必須

    **権限**: チャンネルメンバー（Phase 5で実装予定、現在は全ユーザー可能）

    **Args:**
        channel_id: チャンネルID
        message_data: メッセージ作成データ
            - content: メッセージ内容（1文字以上）
        current_user: 認証済みユーザー
        db: データベースセッション

    **Returns:**
        MessageWithSender: 作成されたメッセージ情報（送信者情報付き）

    **Raises:**
        404: チャンネルが存在しない場合
        401: 未認証の場合
    """
    # チャンネル存在チェック
    channel = get_channel_by_id(db, channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel with id {channel_id} not found"
        )

    # メッセージ作成
    message = create_channel_message(db, channel_id, message_data, current_user.id)

    # 送信者情報付きでレスポンス
    return MessageWithSender(
        id=message.id,
        content=message.content,
        sender_id=message.sender_id,
        sender_username=current_user.username,
        channel_id=message.channel_id,
        receiver_id=message.receiver_id,
        created_at=message.created_at
    )


@router.get("/{channel_id}/messages", response_model=List[MessageWithSender])
async def get_channel_message_history(
    channel_id: int,
    limit: int = Query(default=100, ge=1, le=500, description="取得件数（1-500）"),
    offset: int = Query(default=0, ge=0, description="オフセット（ページネーション用）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    チャンネルのメッセージ履歴を取得する

    v3仕様書: GET /channels/{channel_id}/messages

    **認証**: 必須

    **権限**: チャンネルメンバー（Phase 5で実装予定、現在は全ユーザー可能）

    **Args:**
        channel_id: チャンネルID
        limit: 取得件数上限（デフォルト100、最大500）
        offset: オフセット（ページネーション用、デフォルト0）
        current_user: 認証済みユーザー
        db: データベースセッション

    **Returns:**
        List[MessageWithSender]: メッセージリスト（降順、新しいメッセージが先頭）

        各メッセージには以下が含まれます:
            - id: メッセージID
            - content: メッセージ内容
            - sender_id: 送信者のユーザーID
            - sender_username: 送信者のユーザー名
            - channel_id: チャンネルID
            - created_at: 作成日時

    **Raises:**
        404: チャンネルが存在しない場合
        401: 未認証の場合
        400: limit/offsetパラメータが不正な場合

    **Example:**
        ```
        GET /channels/1/messages?limit=50&offset=0
        ```
    """
    # チャンネル存在チェック
    channel = get_channel_by_id(db, channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel with id {channel_id} not found"
        )

    # メッセージ取得（送信者情報付き）
    messages = get_channel_messages_with_sender(db, channel_id, limit, offset)

    # 辞書リストをPydanticモデルに変換
    return [MessageWithSender(**msg) for msg in messages]


# ===== チャンネルメンバー管理 =====

@router.post("/{channel_id}/members", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_member_to_channel(
    channel_id: int,
    request: MemberAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    チャンネルにメンバーを追加する

    POST /channels/{channel_id}/members

    **認証**: 必須

    **Args:**
        channel_id: チャンネルID
        user_id: 追加するユーザーのID (request body)
        current_user: 認証済みユーザー
        db: データベースセッション

    **Returns:**
        {"success": true, "message": "Member added successfully"}

    **Raises:**
        404: チャンネルまたはユーザーが存在しない場合
        400: すでにメンバーの場合
        401: 未認証の場合
    """
    from app.db.create import add_channel_member
    import uuid

    # チャンネル存在チェック
    channel = get_channel_by_id(db, channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel with id {channel_id} not found"
        )

    # ユーザー存在チェック
    try:
        user_uuid = uuid.UUID(request.user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format"
        )

    user = get_user_by_id(db, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {request.user_id} not found"
        )

    # メンバー追加
    try:
        add_channel_member(db, channel_id, user_uuid)
        return {"success": True, "message": "Member added successfully"}
    except Exception as e:
        if "already a member" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add member: {str(e)}"
        )

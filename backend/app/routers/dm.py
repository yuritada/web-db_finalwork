"""
ダイレクトメッセージ (DM) API エンドポイント (v3)
v3仕様書 セクション5.5 準拠
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.connect import get_session
from app.db.create import create_dm_message
from app.db.read import get_user_by_id, get_dm_messages, get_dm_conversations
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.channel import DMCreate, MessagePublic, DMConversation

router = APIRouter(prefix="/messages/dm", tags=["Direct Messages"])


@router.post("", response_model=MessagePublic, status_code=status.HTTP_201_CREATED)
async def send_dm(
    dm_data: DMCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    DMを送信する

    v3仕様書: POST /messages/dm

    **認証**: 必須

    **Args:**
        dm_data: DM作成データ
            - receiver_id: 受信者のユーザーID
            - content: メッセージ内容（1文字以上）
        current_user: 認証済みユーザー（送信者）
        db: データベースセッション

    **Returns:**
        MessagePublic: 作成されたDMメッセージ情報

    **Raises:**
        404: 受信者ユーザーが存在しない場合
        400: 自分自身にDMを送信しようとした場合
        401: 未認証の場合

    **Example:**
        ```json
        POST /messages/dm
        {
            "receiver_id": "550e8400-e29b-41d4-a716-446655440000",
            "content": "Hello, how are you?"
        }
        ```
    """
    # 受信者存在チェック
    receiver = get_user_by_id(db, dm_data.receiver_id)
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {dm_data.receiver_id} not found"
        )

    # 自分自身へのDM防止
    if current_user.id == dm_data.receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send DM to yourself"
        )

    # DM作成
    message = create_dm_message(db, dm_data, current_user.id)
    return message


@router.get("/{user_id}", response_model=List[MessagePublic])
async def get_dm_history(
    user_id: uuid.UUID,
    limit: int = Query(default=100, ge=1, le=500, description="取得件数（1-500）"),
    offset: int = Query(default=0, ge=0, description="オフセット（ページネーション用）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    特定ユーザーとのDM履歴を取得する

    v3仕様書: GET /messages/dm/{user_id}

    **認証**: 必須

    **Args:**
        user_id: 相手ユーザーのID
        limit: 取得件数上限（デフォルト100、最大500）
        offset: オフセット（ページネーション用、デフォルト0）
        current_user: 認証済みユーザー
        db: データベースセッション

    **Returns:**
        List[MessagePublic]: メッセージリスト（降順、新しいメッセージが先頭）

        各メッセージには以下が含まれます:
            - id: メッセージID
            - content: メッセージ内容
            - sender_id: 送信者のユーザーID
            - receiver_id: 受信者のユーザーID
            - channel_id: null（DMの場合）
            - created_at: 作成日時

    **Raises:**
        404: 相手ユーザーが存在しない場合
        401: 未認証の場合
        400: limit/offsetパラメータが不正な場合

    **Example:**
        ```
        GET /messages/dm/550e8400-e29b-41d4-a716-446655440000?limit=50&offset=0
        ```
    """
    # 相手ユーザー存在チェック
    other_user = get_user_by_id(db, user_id)
    if not other_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # DM履歴取得（双方向）
    messages = get_dm_messages(db, current_user.id, user_id, limit, offset)
    return messages


@router.get("", response_model=List[DMConversation])
async def get_dm_conversation_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    DM会話一覧を取得する（v3拡張機能）

    **認証**: 必須

    Note: この機能はv3仕様書には明示されていませんが、
    フロントエンドでのDM一覧表示のために実装されています。

    **Args:**
        current_user: 認証済みユーザー
        db: データベースセッション

    **Returns:**
        List[DMConversation]: DM会話一覧（最新メッセージ順）

        各会話には以下が含まれます:
            - user_id: 相手ユーザーのID
            - username: 相手ユーザーのユーザー名
            - last_message: 最新メッセージ内容（なければnull）
            - last_message_at: 最新メッセージ日時（なければnull）
            - unread_count: 未読メッセージ数（将来実装予定、現在は常に0）

    **Raises:**
        401: 未認証の場合

    **Example:**
        ```
        GET /messages/dm
        ```

        **Response:**
        ```json
        [
            {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "alice",
                "last_message": "See you tomorrow!",
                "last_message_at": "2025-01-10T14:30:00",
                "unread_count": 0
            },
            {
                "user_id": "660e8400-e29b-41d4-a716-446655440111",
                "username": "bob",
                "last_message": "Thanks for your help",
                "last_message_at": "2025-01-09T10:15:00",
                "unread_count": 0
            }
        ]
        ```
    """
    conversations = get_dm_conversations(db, current_user.id)
    return [DMConversation(**conv) for conv in conversations]

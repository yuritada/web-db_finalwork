"""
READ operations (v3)
"""
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from app.models.user import User
from app.models.wiki import WikiPage, WikiPagePermission
from app.models.tag import Tag, UserTag
from app.models.channel import Channel
from app.models.message import Message
from sqlalchemy import or_, and_


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """ユーザー名でユーザーを取得"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """IDでユーザーを取得"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """メールアドレスでユーザーを取得"""
    return db.query(User).filter(User.email == email).first()


# Wiki関連の読み取り操作

def get_wiki_page_by_id(db: Session, page_id: int) -> Optional[WikiPage]:
    """WikiページIDでページを取得"""
    return db.query(WikiPage).filter(WikiPage.id == page_id).first()


def get_wiki_permission(
    db: Session,
    user_id: uuid.UUID,
    page_id: int
) -> Optional[WikiPagePermission]:
    """ユーザーのWikiページ権限を取得"""
    return db.query(WikiPagePermission).filter(
        WikiPagePermission.user_id == user_id,
        WikiPagePermission.page_id == page_id
    ).first()


def get_wiki_pages_for_user(db: Session, user_id: uuid.UUID) -> List[WikiPage]:
    """ユーザーが閲覧権限を持つWikiページ一覧を取得"""
    # WikiPagePermissionテーブルからユーザーが権限を持つpage_idを取得
    permitted_page_ids = db.query(WikiPagePermission.page_id).filter(
        WikiPagePermission.user_id == user_id
    ).all()

    page_ids = [page_id for (page_id,) in permitted_page_ids]

    if not page_ids:
        return []

    # 権限を持つページを取得
    return db.query(WikiPage).filter(WikiPage.id.in_(page_ids)).all()


# Tag関連の読み取り操作

def get_tag_by_id(db: Session, tag_id: int) -> Optional[Tag]:
    """タグIDでタグを取得"""
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_all_tags(db: Session) -> List[Tag]:
    """すべてのタグを取得"""
    return db.query(Tag).order_by(Tag.id).all()


def get_tags_for_user(db: Session, user_id: uuid.UUID) -> List[Tag]:
    """ユーザーに割り当てられたタグ一覧を取得"""
    # UserTagテーブルからユーザーに割り当てられたtag_idを取得
    assigned_tag_ids = db.query(UserTag.tag_id).filter(
        UserTag.user_id == user_id
    ).all()

    tag_ids = [tag_id for (tag_id,) in assigned_tag_ids]

    if not tag_ids:
        return []

    # タグを取得
    return db.query(Tag).filter(Tag.id.in_(tag_ids)).all()


# Search関連の読み取り操作

def search_wiki_pages(db: Session, query: str, user_id: uuid.UUID) -> List[WikiPage]:
    """
    Wikiページを検索（権限チェック付き）

    ユーザーが閲覧権限を持つWikiページのうち、
    タイトルまたは本文に検索キーワードを含むものを返す

    Args:
        db: データベースセッション
        query: 検索キーワード
        user_id: ユーザーID

    Returns:
        検索結果のWikiページリスト
    """
    # ユーザーが権限を持つpage_idを取得
    permitted_page_ids = db.query(WikiPagePermission.page_id).filter(
        WikiPagePermission.user_id == user_id
    ).all()

    page_ids = [page_id for (page_id,) in permitted_page_ids]

    if not page_ids:
        return []

    # 権限を持つページの中から、タイトルまたは本文に検索キーワードを含むものを検索
    search_pattern = f"%{query}%"
    return db.query(WikiPage).filter(
        WikiPage.id.in_(page_ids),
        (WikiPage.title.ilike(search_pattern)) | (WikiPage.content.ilike(search_pattern))
    ).all()


def search_tags(db: Session, query: str) -> List[Tag]:
    """
    タグを検索（タグ名の部分一致）

    Args:
        db: データベースセッション
        query: 検索キーワード

    Returns:
        検索結果のタグリスト
    """
    search_pattern = f"%{query}%"
    return db.query(Tag).filter(Tag.name.ilike(search_pattern)).all()


def search_users(db: Session, query: str) -> List[User]:
    """
    ユーザーを検索（ユーザー名またはメールアドレスの部分一致）

    Args:
        db: データベースセッション
        query: 検索キーワード

    Returns:
        検索結果のユーザーリスト
    """
    search_pattern = f"%{query}%"
    return db.query(User).filter(
        (User.username.ilike(search_pattern)) | (User.email.ilike(search_pattern))
    ).all()


# Channel関連の読み取り操作

def get_all_channels(db: Session) -> List[Channel]:
    """
    全チャンネルを取得する

    Note: v3仕様書では権限管理なし（全ユーザーが全チャンネル閲覧可能）
    将来的にはis_privateに基づく権限チェックを追加予定

    Args:
        db: データベースセッション

    Returns:
        Channelオブジェクトのリスト
    """
    return db.query(Channel).order_by(Channel.id).all()


def get_channel_by_id(db: Session, channel_id: int) -> Optional[Channel]:
    """
    チャンネルIDでチャンネルを取得する

    Args:
        db: データベースセッション
        channel_id: チャンネルID

    Returns:
        Channelオブジェクト、存在しない場合はNone
    """
    return db.query(Channel).filter(Channel.id == channel_id).first()


def get_channel_by_name(db: Session, channel_name: str) -> Optional[Channel]:
    """
    チャンネル名でチャンネルを取得する

    Args:
        db: データベースセッション
        channel_name: チャンネル名

    Returns:
        Channelオブジェクト、存在しない場合はNone
    """
    return db.query(Channel).filter(Channel.name == channel_name).first()


# Message関連の読み取り操作

def get_channel_messages(
    db: Session,
    channel_id: int,
    limit: int = 100,
    offset: int = 0
) -> List[Message]:
    """
    チャンネルのメッセージ履歴を取得する（新しい順）

    Args:
        db: データベースセッション
        channel_id: チャンネルID
        limit: 取得件数上限（デフォルト100）
        offset: オフセット（ページネーション用）

    Returns:
        Messageオブジェクトのリスト（降順、新しいメッセージが先頭）
    """
    return db.query(Message).filter(
        Message.channel_id == channel_id
    ).order_by(
        Message.created_at.desc()
    ).limit(limit).offset(offset).all()


def get_channel_messages_with_sender(
    db: Session,
    channel_id: int,
    limit: int = 100,
    offset: int = 0
) -> List[dict]:
    """
    チャンネルのメッセージ履歴を送信者情報付きで取得する

    Args:
        db: データベースセッション
        channel_id: チャンネルID
        limit: 取得件数上限（デフォルト100）
        offset: オフセット（ページネーション用）

    Returns:
        辞書のリスト（Message + sender.username）
    """
    results = db.query(
        Message,
        User.username
    ).join(
        User, Message.sender_id == User.id
    ).filter(
        Message.channel_id == channel_id
    ).order_by(
        Message.created_at.desc()
    ).limit(limit).offset(offset).all()

    return [
        {
            "id": msg.id,
            "content": msg.content,
            "sender_id": msg.sender_id,
            "sender_username": username,
            "channel_id": msg.channel_id,
            "receiver_id": msg.receiver_id,
            "created_at": msg.created_at
        }
        for msg, username in results
    ]


def get_dm_messages(
    db: Session,
    user_id1: uuid.UUID,
    user_id2: uuid.UUID,
    limit: int = 100,
    offset: int = 0
) -> List[Message]:
    """
    2ユーザー間のDM履歴を取得する（新しい順）

    Args:
        db: データベースセッション
        user_id1: ユーザー1のID（通常は現在ログインしているユーザー）
        user_id2: ユーザー2のID
        limit: 取得件数上限（デフォルト100）
        offset: オフセット（ページネーション用）

    Returns:
        Messageオブジェクトのリスト（降順、新しいメッセージが先頭）
    """
    return db.query(Message).filter(
        and_(
            Message.channel_id.is_(None),  # DM判定
            or_(
                and_(
                    Message.sender_id == user_id1,
                    Message.receiver_id == user_id2
                ),
                and_(
                    Message.sender_id == user_id2,
                    Message.receiver_id == user_id1
                )
            )
        )
    ).order_by(
        Message.created_at.desc()
    ).limit(limit).offset(offset).all()


def get_dm_conversations(db: Session, user_id: uuid.UUID) -> List[dict]:
    """
    ユーザーのDM会話一覧を取得する

    Args:
        db: データベースセッション
        user_id: ユーザーID

    Returns:
        DM会話リスト（相手ユーザー情報 + 最新メッセージ）
    """
    # ユーザーが送信または受信したDMの相手ユーザーIDを取得
    sent_to = db.query(Message.receiver_id).filter(
        and_(
            Message.sender_id == user_id,
            Message.channel_id.is_(None)
        )
    ).distinct().all()

    received_from = db.query(Message.sender_id).filter(
        and_(
            Message.receiver_id == user_id,
            Message.channel_id.is_(None)
        )
    ).distinct().all()

    # 相手ユーザーIDを統合（重複除去）
    partner_ids = set([uid for (uid,) in sent_to] + [uid for (uid,) in received_from])

    conversations = []
    for partner_id in partner_ids:
        # 相手ユーザー情報取得
        partner = get_user_by_id(db, partner_id)
        if not partner:
            continue

        # 最新メッセージ取得
        latest_message = db.query(Message).filter(
            and_(
                Message.channel_id.is_(None),
                or_(
                    and_(
                        Message.sender_id == user_id,
                        Message.receiver_id == partner_id
                    ),
                    and_(
                        Message.sender_id == partner_id,
                        Message.receiver_id == user_id
                    )
                )
            )
        ).order_by(Message.created_at.desc()).first()

        conversations.append({
            "user_id": partner.id,
            "username": partner.username,
            "last_message": latest_message.content if latest_message else None,
            "last_message_at": latest_message.created_at if latest_message else None,
            "unread_count": 0  # 将来実装予定
        })

    # 最新メッセージ日時でソート（降順）
    conversations.sort(
        key=lambda x: x["last_message_at"] if x["last_message_at"] else "1970-01-01",
        reverse=True
    )

    return conversations


# Channel membership operations

def get_channel_members(db: Session, channel_id: int) -> List[dict]:
    """
    チャンネルのメンバーリストを取得

    Args:
        db: データベースセッション
        channel_id: チャンネルID

    Returns:
        メンバー情報のリスト（ユーザーID、ユーザー名、メールアドレス）
    """
    from app.models.channel_membership import ChannelMembership

    memberships = db.query(ChannelMembership).filter(
        ChannelMembership.channel_id == channel_id
    ).all()

    members = []
    for membership in memberships:
        user = get_user_by_id(db, membership.user_id)
        if user:
            members.append({
                "id": str(user.id),
                "username": user.username,
                "email": user.email
            })

    return members


def is_channel_member(db: Session, user_id: uuid.UUID, channel_id: int) -> bool:
    """
    ユーザーがチャンネルのメンバーかどうかを確認

    Args:
        db: データベースセッション
        user_id: ユーザーID
        channel_id: チャンネルID

    Returns:
        メンバーならTrue、それ以外False
    """
    from app.models.channel_membership import ChannelMembership

    membership = db.query(ChannelMembership).filter(
        ChannelMembership.user_id == user_id,
        ChannelMembership.channel_id == channel_id
    ).first()

    return membership is not None

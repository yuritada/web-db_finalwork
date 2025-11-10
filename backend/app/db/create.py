"""
CREATE operations (v3)
"""
from sqlalchemy.orm import Session
import bcrypt
import uuid

from app.models.user import User, UserKategori
from app.models.wiki import WikiPage, WikiPagePermission, PermissionLevel
from app.models.tag import Tag, UserTag
from app.models.channel import Channel
from app.models.message import Message
from app.schemas.user import UserCreate
from app.schemas.wiki import WikiPageCreate
from app.schemas.tag import TagCreate
from app.schemas.channel import ChannelCreate, MessageCreate, DMCreate


def hash_password(password: str) -> str:
    """パスワードをハッシュ化する（bcrypt直接使用）"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    ユーザーを作成する（v3ロジック）

    【v3変更点】
    - 教員/事務の場合、gakuseki_bangoに自動生成文字列を設定
    - 学生の場合、gakuseki_bangoはリクエストボディの値をそのまま使用
    """
    # パスワードをハッシュ化
    hashed_pw = hash_password(user_data.password)

    # gakuseki_bangoの処理（v3ロジック）
    gakuseki_bango = user_data.gakuseki_bango

    # 学生以外の場合、自動生成
    if user_data.kategori != UserKategori.STUDENT:
        gakuseki_bango = f"staff_{uuid.uuid4().hex[:8]}"

    # Userモデルのインスタンスを作成
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
        kategori=user_data.kategori,
        gakuseki_bango=gakuseki_bango,
        faculty=user_data.faculty
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# Wiki関連の作成操作

def create_wiki_page(
    db: Session,
    page_data: WikiPageCreate,
    creator_id: uuid.UUID
) -> WikiPage:
    """
    Wikiページを作成する（v3ロジック）

    【v3仕様】
    - ページ作成時、作成者に自動的にEDIT権限を付与
    """
    # WikiPageモデルのインスタンスを作成
    db_page = WikiPage(
        title=page_data.title,
        content=page_data.content,
        creator_id=creator_id
    )

    db.add(db_page)
    db.flush()  # IDを取得するためflush

    # 作成者にEDIT権限を自動付与
    creator_permission = WikiPagePermission(
        page_id=db_page.id,
        user_id=creator_id,
        permission_level=PermissionLevel.EDIT
    )

    db.add(creator_permission)
    db.commit()
    db.refresh(db_page)

    return db_page


def share_wiki_page(
    db: Session,
    page_id: int,
    user_id: uuid.UUID,
    permission_level: PermissionLevel
) -> WikiPagePermission:
    """
    Wikiページの権限を追加または更新する

    既存の権限がある場合は更新、ない場合は新規作成
    """
    # 既存の権限を確認
    existing_permission = db.query(WikiPagePermission).filter(
        WikiPagePermission.page_id == page_id,
        WikiPagePermission.user_id == user_id
    ).first()

    if existing_permission:
        # 既存の権限を更新
        existing_permission.permission_level = permission_level
        db.commit()
        db.refresh(existing_permission)
        return existing_permission
    else:
        # 新規権限を作成
        new_permission = WikiPagePermission(
            page_id=page_id,
            user_id=user_id,
            permission_level=permission_level
        )
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)
        return new_permission


# Tag関連の作成操作

def create_tag(
    db: Session,
    tag_data: TagCreate,
    creator_id: uuid.UUID
) -> Tag:
    """
    タグを作成する（v3ロジック）

    【v3仕様】
    - タグ作成時、creator_idを記録
    """
    # Tagモデルのインスタンスを作成
    db_tag = Tag(
        name=tag_data.name,
        creator_id=creator_id
    )

    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)

    return db_tag


def assign_tag_to_user(
    db: Session,
    tag_id: int,
    user_id: uuid.UUID
) -> UserTag:
    """
    ユーザーにタグを割り当てる

    既存の割り当てがある場合は何もしない（冪等性）
    """
    # 既存の割り当てを確認
    existing_assignment = db.query(UserTag).filter(
        UserTag.tag_id == tag_id,
        UserTag.user_id == user_id
    ).first()

    if existing_assignment:
        # 既に割り当て済みの場合はそのまま返す
        return existing_assignment

    # 新規割り当てを作成
    new_assignment = UserTag(
        tag_id=tag_id,
        user_id=user_id
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment


# Channel関連の作成操作

def create_channel(db: Session, channel_data: ChannelCreate) -> Channel:
    """
    チャンネルを作成する

    Args:
        db: データベースセッション
        channel_data: チャンネル作成データ

    Returns:
        作成されたChannelオブジェクト

    Raises:
        IntegrityError: チャンネル名が既に存在する場合
    """
    db_channel = Channel(
        name=channel_data.name,
        description=channel_data.description,
        is_private=channel_data.is_private
    )

    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)

    return db_channel


# Message関連の作成操作

def create_channel_message(
    db: Session,
    channel_id: int,
    message_data: MessageCreate,
    sender_id: uuid.UUID
) -> Message:
    """
    チャンネルメッセージを作成する

    Args:
        db: データベースセッション
        channel_id: チャンネルID
        message_data: メッセージ作成データ
        sender_id: 送信者のユーザーID

    Returns:
        作成されたMessageオブジェクト
    """
    db_message = Message(
        content=message_data.content,
        sender_id=sender_id,
        channel_id=channel_id,
        receiver_id=None  # チャンネルメッセージはNULL
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message


def create_dm_message(
    db: Session,
    dm_data: DMCreate,
    sender_id: uuid.UUID
) -> Message:
    """
    DMを作成する

    Args:
        db: データベースセッション
        dm_data: DM作成データ
        sender_id: 送信者のユーザーID

    Returns:
        作成されたMessageオブジェクト
    """
    db_message = Message(
        content=dm_data.content,
        sender_id=sender_id,
        channel_id=None,  # DMはNULL
        receiver_id=dm_data.receiver_id
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message

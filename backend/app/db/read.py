"""
READ operations (v3)
"""
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from app.models.user import User
from app.models.wiki import WikiPage, WikiPagePermission
from app.models.tag import Tag, UserTag


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

"""
DELETE operations (v3)
"""
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.models.tag import Tag, UserTag
from app.models.wiki import WikiPagePermission


def delete_tag(db: Session, tag_id: int) -> bool:
    """
    タグを削除する

    Args:
        db: データベースセッション
        tag_id: タグID

    Returns:
        削除に成功した場合True、タグが存在しない場合False

    Note:
        UserTagsは CASCADE DELETE により自動削除される
    """
    # タグを取得
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()

    if not db_tag:
        return False

    # タグを削除（UserTagsも自動削除される）
    db.delete(db_tag)
    db.commit()

    return True


def remove_wiki_permission(db: Session, page_id: int, user_id: uuid.UUID) -> bool:
    """
    Wiki権限を削除する（共有解除）

    Args:
        db: データベースセッション
        page_id: WikiページID
        user_id: ユーザーID

    Returns:
        削除に成功した場合True、権限が存在しない場合False
    """
    # 権限を取得
    permission = db.query(WikiPagePermission).filter(
        WikiPagePermission.page_id == page_id,
        WikiPagePermission.user_id == user_id
    ).first()

    if not permission:
        return False

    # 権限を削除
    db.delete(permission)
    db.commit()

    return True


def remove_tag_assignment(db: Session, tag_id: int, user_id: uuid.UUID) -> bool:
    """
    タグの割り当てを解除する

    Args:
        db: データベースセッション
        tag_id: タグID
        user_id: ユーザーID

    Returns:
        削除に成功した場合True、割り当てが存在しない場合False
    """
    # タグ割り当てを取得
    user_tag = db.query(UserTag).filter(
        UserTag.tag_id == tag_id,
        UserTag.user_id == user_id
    ).first()

    if not user_tag:
        return False

    # タグ割り当てを削除
    db.delete(user_tag)
    db.commit()

    return True

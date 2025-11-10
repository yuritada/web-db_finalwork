"""
DELETE operations (v3)
"""
from sqlalchemy.orm import Session
from typing import Optional

from app.models.tag import Tag


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

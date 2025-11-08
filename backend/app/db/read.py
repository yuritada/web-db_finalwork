"""
READ operations (v3)
"""
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.models.user import User


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """ユーザー名でユーザーを取得"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """IDでユーザーを取得"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """メールアドレスでユーザーを取得"""
    return db.query(User).filter(User.email == email).first()

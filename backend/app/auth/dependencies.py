"""
Authentication dependencies for FastAPI routes and WebSocket
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
import os

from app.db.connect import get_session
from app.db.read import get_user_by_username, get_user_by_id
from app.models.user import User
import uuid as uuid_lib

# OAuth2スキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# 環境変数から取得
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session)
) -> User:
    """
    JWTトークンから現在のユーザーを取得（HTTP API用）

    Args:
        token: JWTアクセストークン
        db: データベースセッション

    Returns:
        認証されたユーザー

    Raises:
        HTTPException: 認証に失敗した場合
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # トークンをデコード
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        # user_idをUUIDに変換
        try:
            user_id = uuid_lib.UUID(user_id_str)
        except ValueError:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # ユーザーを取得
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_ws(token: str, db: Session) -> Optional[User]:
    """
    JWTトークンから現在のユーザーを取得（WebSocket用）

    Args:
        token: JWTアクセストークン
        db: データベースセッション

    Returns:
        認証されたユーザー、失敗時はNone
    """
    try:
        # トークンをデコード
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            return None

        # user_idをUUIDに変換
        try:
            user_id = uuid_lib.UUID(user_id_str)
        except ValueError:
            return None

        # ユーザーを取得
        user = get_user_by_id(db, user_id)
        return user

    except JWTError:
        return None

"""
Dependency injection components (v3)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Annotated

from app.db.connect import get_session
from app.db.read import get_user_by_username
from app.core.config import settings
from app.models.user import User
from app.schemas.token import TokenData

# OAuth2 Bearer トークン認証スキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db_session() -> Session:
    """
    データベースセッションを取得する依存関数
    FastAPIのDependsで使用される
    """
    return Depends(get_session)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_session)
) -> User:
    """
    JWTトークンを検証して現在のユーザーを返す（v3）

    Args:
        token: Bearer トークン
        db: データベースセッション

    Returns:
        User: 認証されたユーザー

    Raises:
        HTTPException: トークンが無効な場合（401）
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # JWTトークンをデコード
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # データベースからユーザーを取得
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user

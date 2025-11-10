"""
Dependency injection components (v3)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Annotated
import uuid

from app.db.connect import get_session
from app.db.read import get_user_by_username, get_user_by_id, get_wiki_permission, get_tag_by_id
from app.core.config import settings
from app.models.user import User, UserKategori
from app.models.wiki import PermissionLevel
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
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        # UUIDにパース（auth.pyで user.id を str() したものを復元）
        try:
            user_id = uuid.UUID(user_id_str)
        except (ValueError, AttributeError):
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # データベースからユーザーを取得（user.id で検索）
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


# Wiki権限チェック

async def check_wiki_view_permission(
    page_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> User:
    """
    Wikiページの閲覧権限（VIEW_ONLY以上）をチェック

    Args:
        page_id: WikiページID
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        User: 認証されたユーザー（権限がある場合）

    Raises:
        HTTPException: 権限がない場合（403）
    """
    permission = get_wiki_permission(db, current_user.id, page_id)

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this page"
        )

    # VIEW_ONLYもしくはEDIT権限があればOK
    return current_user


async def check_wiki_edit_permission(
    page_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> User:
    """
    Wikiページの編集権限（EDIT）をチェック

    Args:
        page_id: WikiページID
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        User: 認証されたユーザー（権限がある場合）

    Raises:
        HTTPException: 権限がない場合（403）
    """
    permission = get_wiki_permission(db, current_user.id, page_id)

    if not permission or permission.permission_level != PermissionLevel.EDIT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this page"
        )

    return current_user


# Tag権限チェック

async def check_tag_assign_permission(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> User:
    """
    タグ割り当て権限をチェック（v3ロジック）

    【v3権限ロジック】
    - 学生: 誰にでもタグ割り当て可能
    - 教員: 自分が作成したタグのみ割り当て可能

    Args:
        tag_id: タグID
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        User: 認証されたユーザー（権限がある場合）

    Raises:
        HTTPException: 権限がない場合（403）、タグが存在しない場合（404）
    """
    # タグの存在確認
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # 学生の場合は常に許可
    if current_user.kategori == UserKategori.STUDENT:
        return current_user

    # 教員の場合は自分が作成したタグのみ許可
    if tag.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only assign tags that you created"
        )

    return current_user

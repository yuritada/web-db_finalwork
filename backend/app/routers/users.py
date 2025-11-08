"""
User API endpoints (v3)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserPublicWithTags

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublicWithTags)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    現在のユーザー情報を取得（v3）

    認証済みユーザーの情報とタグ情報を返す

    Returns:
        UserPublicWithTags: ユーザー情報（タグ含む）
    """
    return current_user

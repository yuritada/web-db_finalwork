"""
User schemas (v3)
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid

from app.models.user import UserKategori


class UserBase(BaseModel):
    """ユーザーの基本情報"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    kategori: UserKategori
    gakuseki_bango: Optional[str] = Field(None, max_length=50)
    faculty: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """ユーザー登録用スキーマ"""
    password: str = Field(..., min_length=8)


class UserPublic(UserBase):
    """ユーザー公開情報"""
    id: uuid.UUID
    icon_path: Optional[str] = None

    model_config = {"from_attributes": True}


class UserInfo(BaseModel):
    """ユーザー基本情報（API連携用）"""
    id: uuid.UUID
    username: str
    email: str

    model_config = {"from_attributes": True}


class UserPublicWithTags(UserPublic):
    """タグ情報を含むユーザー公開情報"""
    tags: List["TagPublic"] = []

    model_config = {"from_attributes": True}


# 循環インポートを避けるために後で定義
from app.schemas.tag import TagPublic  # noqa: E402
UserPublicWithTags.model_rebuild()

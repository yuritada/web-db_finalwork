"""
Wiki schemas (v3)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.wiki import PermissionLevel


class WikiPageBase(BaseModel):
    """Wikiページの基本情報"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(default="")


class WikiPageCreate(WikiPageBase):
    """Wikiページ作成用スキーマ"""
    pass


class WikiPageUpdate(BaseModel):
    """Wikiページ更新用スキーマ"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None


class WikiPagePublic(WikiPageBase):
    """Wikiページ公開情報"""
    id: int
    creator_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PermissionInfo(BaseModel):
    """権限情報"""
    user_id: uuid.UUID
    permission_level: PermissionLevel

    model_config = {"from_attributes": True}


class WikiPageDetail(WikiPagePublic):
    """Wikiページ詳細（権限情報含む）"""
    permissions: List[PermissionInfo] = []

    model_config = {"from_attributes": True}


class PermissionSet(BaseModel):
    """権限設定用スキーマ"""
    user_id: uuid.UUID
    permission_level: PermissionLevel

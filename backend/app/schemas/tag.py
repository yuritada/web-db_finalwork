"""
Tag schemas (v3)
"""
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid


class TagBase(BaseModel):
    """タグの基本情報"""
    name: str = Field(..., min_length=1, max_length=100)


class TagCreate(TagBase):
    """タグ作成用スキーマ"""
    pass


class TagUpdate(BaseModel):
    """タグ更新用スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class TagPublic(TagBase):
    """タグ公開情報"""
    id: int
    creator_id: uuid.UUID

    model_config = {"from_attributes": True}


class UserInfo(BaseModel):
    """タグ詳細で使用するユーザー情報"""
    id: uuid.UUID
    username: str
    email: str

    model_config = {"from_attributes": True}


class TagDetail(TagPublic):
    """タグ詳細情報（割り当てられたユーザーリスト含む）"""
    assigned_users: List[UserInfo] = []


class TagAssignment(BaseModel):
    """タグ割り当て用スキーマ"""
    user_id: uuid.UUID


class TagAssign(BaseModel):
    """タグ割り当て/削除用スキーマ（後方互換）"""
    user_id: uuid.UUID
    tag_id: int

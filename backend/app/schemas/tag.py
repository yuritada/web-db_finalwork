"""
Tag schemas (v3)
"""
from pydantic import BaseModel, Field
import uuid


class TagBase(BaseModel):
    """タグの基本情報"""
    name: str = Field(..., min_length=1, max_length=100)


class TagCreate(TagBase):
    """タグ作成用スキーマ"""
    pass


class TagPublic(TagBase):
    """タグ公開情報"""
    id: int
    creator_id: uuid.UUID

    model_config = {"from_attributes": True}


class TagAssign(BaseModel):
    """タグ割り当て/削除用スキーマ"""
    user_id: uuid.UUID
    tag_id: int

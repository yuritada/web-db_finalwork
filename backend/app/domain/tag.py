from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Optional

# --- Enums (列挙型) の定義 ---

class TagType(str, Enum):
    """
    タグの種類
    """
    OFFICIAL = "official"     # 運営・教員が作成する公式タグ (例: "1年生", "MUDS")
    USER_DEFINED = "user_defined" # ユーザーが自由に作成できるタグ (例: "AI勉強中")

class Tag(BaseModel):
    """
    タグのドメインモデル (エンティティ)
    ユーザーに付与できるタグ情報を表します。
    """
    id: UUID = Field(default_factory=uuid4, description="一意のタグID (PK)")
    
    name: str = Field(..., max_length=50, description="タグの名前 (例: '1年生', 'AI勉強中')")
    
    tag_type: TagType = Field(default=TagType.USER_DEFINED, description="タグの種類 (公式 or ユーザー定義)")
    
    # ご提案の「変更権限」に相当。
    # OFFICIALタグは特定のロール（例: STAFF）しか作成・削除できない、
    # といったロジックをユースケース層で実装するための判断材料になります。
    
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")

    model_config = ConfigDict(
        from_attributes=True  # 'orm_mode = True' の V2 での名称
    )
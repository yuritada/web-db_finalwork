from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Optional # Optional をインポート

class UserRole(str, Enum):
    """
    ユーザーの区分（役割）
    """
    STUDENT = "student"         # 学生
    PROFESSOR = "professor"     # 教授
    ASSOCIATE_PROFESSOR = "associate_professor" # 准教授
    LECTURER = "lecturer"       # 講師
    STAFF = "staff"             # 事務
    
class Faculty(str, Enum):
    """
    所属学部
    """
    MUDS = "muds" # 武蔵野大学データサイエンス学部
    MIDS = "mids" # 武蔵野大学通信制データサイエンス学部
    # ... 他の学部

# --- ユーザーモデル本体 ---

class User(BaseModel):
    """
    ユーザーのドメインモデル (エンティティ)
    システムの中核となるユーザー情報を表します。
    """
    id: UUID = Field(default_factory=uuid4, description="一意のユーザーID (PK)")
    
    # --- ご提案いただいた要素 ---
    username: str = Field(..., max_length=50, description="表示用のユーザー名 (ご提案の「名前」に相当)")
    
    role: UserRole = Field(..., description="ユーザーの区分 (ご提案の「区分」)")
    
    university_id: str = Field(..., max_length=20, description="学籍番号または教職員番号 (ご提案の「学籍番号」)")
    
    faculty: Optional[Faculty] = Field(None, description="所属学部 (ご提案の「学部」)")
    
    icon_image_path: Optional[str] = Field(None, description="アイコン画像のパス (ご提案の「アイコン写真パス」)")
    
    # --- ログイン・認証情報 ---
    email: EmailStr = Field(..., description="メールアドレス (ログイン用)")
    hashed_password: str = Field(..., description="ハッシュ化されたパスワード")
    
    # --- システムメタデータ ---
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新日時")

    model_config = ConfigDict(
        from_attributes=True  # 'orm_mode = True' の V2 での名称
    )
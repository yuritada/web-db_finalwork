"""
User Model (v3)
"""
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
import uuid
import enum

from .base import Base


class UserKategori(str, enum.Enum):
    """ユーザーカテゴリー（役割）"""
    STUDENT = "学生"
    PROFESSOR = "教授"
    ASSOCIATE_PROFESSOR = "准教授"
    LECTURER = "講師"
    STAFF = "事務"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # v3: Enum型を使用
    kategori: Mapped[UserKategori] = mapped_column(
        SQLEnum(UserKategori, native_enum=False),
        nullable=False
    )

    # v3: 学籍番号は学生以外はNULL許容
    gakuseki_bango: Mapped[Optional[str]] = mapped_column(
        String(50),
        unique=True,
        nullable=True
    )

    faculty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    icon_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    tags: Mapped[List["UserTag"]] = relationship(
        "UserTag",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    created_tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        back_populates="creator",
        foreign_keys="Tag.creator_id"
    )

    wiki_pages: Mapped[List["WikiPage"]] = relationship(
        "WikiPage",
        back_populates="creator",
        foreign_keys="WikiPage.creator_id"
    )

    wiki_permissions: Mapped[List["WikiPagePermission"]] = relationship(
        "WikiPagePermission",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="sender"
    )

    def __repr__(self) -> str:
        return f"<User(username='{self.username}', kategori='{self.kategori}')>"

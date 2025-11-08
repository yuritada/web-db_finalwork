"""
Wiki Model (v3 - 権限管理追加)
"""
from sqlalchemy import String, Text, ForeignKey, Integer, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime
import uuid
import enum

from .base import Base


class PermissionLevel(str, enum.Enum):
    """Wiki権限レベル"""
    VIEW_ONLY = "VIEW_ONLY"
    EDIT = "EDIT"


class WikiPage(Base):
    __tablename__ = "wiki_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # v3: 作成者を記録
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="wiki_pages",
        foreign_keys=[creator_id]
    )

    # v3: 権限管理
    permissions: Mapped[List["WikiPagePermission"]] = relationship(
        "WikiPagePermission",
        back_populates="page",
        cascade="all, delete-orphan"
    )

    files: Mapped[List["File"]] = relationship(
        "File",
        back_populates="wiki_page",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WikiPage(title='{self.title}')>"


class WikiPagePermission(Base):
    """v3新規: Wiki権限管理テーブル"""
    __tablename__ = "wiki_page_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    page_id: Mapped[int] = mapped_column(
        ForeignKey("wiki_pages.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    permission_level: Mapped[PermissionLevel] = mapped_column(
        SQLEnum(PermissionLevel, native_enum=False),
        nullable=False
    )

    # Relationships
    page: Mapped["WikiPage"] = relationship(
        "WikiPage",
        back_populates="permissions"
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="wiki_permissions"
    )

    def __repr__(self) -> str:
        return f"<WikiPagePermission(page_id={self.page_id}, user_id='{self.user_id}', level='{self.permission_level}')>"

"""
Tag Model (v3 - creator_id追加)
"""
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import uuid

from .base import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # v3: タグ作成者を記録
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_tags",
        foreign_keys=[creator_id]
    )

    user_tags: Mapped[List["UserTag"]] = relationship(
        "UserTag",
        back_populates="tag",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Tag(name='{self.name}')>"


class UserTag(Base):
    """ユーザーとタグの中間テーブル"""
    __tablename__ = "user_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="user_tags")

    def __repr__(self) -> str:
        return f"<UserTag(user_id='{self.user_id}', tag_id='{self.tag_id}')>"

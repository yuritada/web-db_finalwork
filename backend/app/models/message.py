"""
Message Model
"""
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime
import uuid

from .base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    sender_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # チャンネルメッセージ or DMメッセージの区別
    channel_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=True
    )

    # DM用: 受信者ID（チャンネルメッセージの場合はNULL）
    receiver_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    sender: Mapped["User"] = relationship(
        "User",
        back_populates="messages",
        foreign_keys=[sender_id]
    )

    channel: Mapped[Optional["Channel"]] = relationship(
        "Channel",
        back_populates="messages"
    )

    files: Mapped[List["File"]] = relationship(
        "File",
        back_populates="message",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, sender_id='{self.sender_id}')>"

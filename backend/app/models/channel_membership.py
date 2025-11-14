"""
Channel Membership Model
多対多の関係: User <-> Channel
"""
from sqlalchemy import Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid

from .base import Base


class ChannelMembership(Base):
    """
    チャンネルメンバーシップテーブル

    ユーザーとチャンネルの多対多の関係を管理
    """
    __tablename__ = "channel_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    channel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # ユニーク制約: 同じユーザーが同じチャンネルに重複して参加できない
    __table_args__ = (
        UniqueConstraint('user_id', 'channel_id', name='uix_user_channel'),
    )

    def __repr__(self) -> str:
        return f"<ChannelMembership(user_id='{self.user_id}', channel_id={self.channel_id})>"

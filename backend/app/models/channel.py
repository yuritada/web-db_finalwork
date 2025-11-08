"""
Channel Model
"""
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from .base import Base


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="channel",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Channel(name='{self.name}', is_private={self.is_private})>"

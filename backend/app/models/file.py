"""
File Model
"""
from sqlalchemy import String, Integer, ForeignKey, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
import uuid

from .base import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)  # バイト単位
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    uploader_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # ファイルが添付されているリソース
    message_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=True
    )

    wiki_page_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("wiki_pages.id", ondelete="CASCADE"),
        nullable=True
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    message: Mapped[Optional["Message"]] = relationship(
        "Message",
        back_populates="files"
    )

    wiki_page: Mapped[Optional["WikiPage"]] = relationship(
        "WikiPage",
        back_populates="files"
    )

    def __repr__(self) -> str:
        return f"<File(filename='{self.filename}')>"

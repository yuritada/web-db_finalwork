"""
SQLAlchemy database connection setup (v3)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# SQLAlchemyエンジンの作成
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # 本番環境ではFalseにする
    pool_pre_ping=True,  # 接続の健全性チェック
    pool_size=5,
    max_overflow=10
)

# セッションファクトリの作成
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_session() -> Generator[Session, None, None]:
    """
    データベースセッションを生成する
    依存性注入で使用される
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

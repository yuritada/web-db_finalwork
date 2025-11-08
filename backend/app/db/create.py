"""
CREATE operations (v3)
"""
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import uuid

from app.models.user import User, UserKategori
from app.schemas.user import UserCreate

# パスワードハッシュ化コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """パスワードをハッシュ化する"""
    return pwd_context.hash(password)


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    ユーザーを作成する（v3ロジック）

    【v3変更点】
    - 教員/事務の場合、gakuseki_bangoに自動生成文字列を設定
    - 学生の場合、gakuseki_bangoはリクエストボディの値をそのまま使用
    """
    # パスワードをハッシュ化
    hashed_pw = hash_password(user_data.password)

    # gakuseki_bangoの処理（v3ロジック）
    gakuseki_bango = user_data.gakuseki_bango

    # 学生以外の場合、自動生成
    if user_data.kategori != UserKategori.STUDENT:
        gakuseki_bango = f"staff_{uuid.uuid4().hex[:8]}"

    # Userモデルのインスタンスを作成
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
        kategori=user_data.kategori,
        gakuseki_bango=gakuseki_bango,
        faculty=user_data.faculty
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

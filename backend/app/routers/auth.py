"""
Authentication API endpoints (v3)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import jwt
from datetime import datetime, timedelta
import bcrypt

from app.db.connect import get_session
from app.db.create import create_user
from app.db.read import get_user_by_username, get_user_by_email
from app.schemas.user import UserCreate, UserPublic
from app.schemas.token import Token
from app.schemas.auth import LoginRequest
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証する（bcrypt直接使用）"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWTアクセストークンを生成する"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_session)
):
    """
    ユーザー登録エンドポイント（v3）

    【v3ロジック】
    - 教員/事務の場合、gakuseki_bangoに自動生成文字列を設定
    - 学生の場合、gakuseki_bangoはリクエストボディの値をそのまま使用
    """
    # ユーザー名の重複チェック
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # メールアドレスの重複チェック
    existing_email = get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # ユーザー作成（v3ロジックがcreate_user内に実装済み）
        db_user = create_user(db, user_data)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e)}"
        )


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    """
    ログインエンドポイント（OAuth2準拠）

    JWTトークンを発行する
    """
    # ユーザー認証
    user = get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # パスワード検証
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # アクセストークン生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  # CRITICAL FIX: user.id を使用（get_current_userと一貫性）
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login_json(
    credentials: LoginRequest,
    db: Session = Depends(get_session)
):
    """
    JSON形式のログインエンドポイント（フロントエンド互換）

    CRITICAL FIX: フロントエンドとの互換性のため、JSON形式を受け付ける

    既存の /auth/token エンドポイント（OAuth2準拠）との違い:
    - リクエスト形式: JSON (application/json)
    - OAuth2準拠: /auth/token は OAuth2PasswordRequestForm (application/x-www-form-urlencoded)

    Args:
        credentials: ログイン認証情報（JSON形式）
            - username: ユーザー名
            - password: パスワード
        db: データベースセッション

    Returns:
        Token: JWTアクセストークン

    Raises:
        401: 認証失敗（ユーザー名またはパスワードが間違っている）
    """
    # ユーザー認証
    user = get_user_by_username(db, credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # パスワード検証
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # アクセストークン生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  # user.idを使用（get_current_userと一貫性）
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")

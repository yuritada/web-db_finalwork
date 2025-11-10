import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import bcrypt

import sys
from pathlib import Path

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from app.db.connect import get_session
from app.models.base import Base
from app.models.user import User, UserKategori
from app.models.wiki import WikiPage
from app.models.tag import Tag
from app.models.channel import Channel
from app.models.message import Message


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Test database session fixture"""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI test client fixture with database override"""
    def override_get_session():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    """Test user fixture (一般ユーザー)"""
    password = "TestPass123!"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed,
        kategori=UserKategori.STUDENT,
        gakuseki_bango="TEST001",
        faculty="工学部"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Add password to user object for testing
    user.plain_password = password

    return user


@pytest.fixture(scope="function")
def student_user(db):
    """Test student user fixture (学生ユーザー)"""
    password = "StudentPass123!"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    user = User(
        username="student",
        email="student@example.com",
        hashed_password=hashed,
        kategori=UserKategori.STUDENT,
        gakuseki_bango="STU001",
        faculty="工学部"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    user.plain_password = password

    return user


@pytest.fixture(scope="function")
def teacher_user(db):
    """Test teacher user fixture (教員ユーザー - 准教授)"""
    password = "TeacherPass123!"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    user = User(
        username="teacher",
        email="teacher@example.com",
        hashed_password=hashed,
        kategori=UserKategori.ASSOCIATE_PROFESSOR,
        gakuseki_bango="staff_teacher1",
        faculty="情報工学科"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    user.plain_password = password

    return user


@pytest.fixture(scope="function")
def other_user(db):
    """Another test user fixture (別のユーザー)"""
    password = "OtherPass123!"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password=hashed,
        kategori=UserKategori.STUDENT,
        gakuseki_bango="OTHER001",
        faculty="理学部"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    user.plain_password = password

    return user


@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    """Authenticated test client fixture"""
    # Login to get token
    response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": test_user.plain_password
        }
    )
    token = response.json()["access_token"]

    # Add authorization header to client
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


# ===== Phase 4: Channels & DM Fixtures =====

@pytest.fixture(scope="function")
def test_channel(db):
    """Test channel fixture (公開チャンネル)"""
    channel = Channel(
        name="Test Channel",
        description="Test channel for pytest",
        is_private=False
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


@pytest.fixture(scope="function")
def private_channel(db):
    """Private channel fixture (プライベートチャンネル)"""
    channel = Channel(
        name="Private Channel",
        description="Private test channel",
        is_private=True
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


@pytest.fixture(scope="function")
def test_channel_message(db, test_user, test_channel):
    """Test channel message fixture (チャンネルメッセージ)"""
    message = Message(
        content="Test channel message",
        sender_id=test_user.id,
        channel_id=test_channel.id
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@pytest.fixture(scope="function")
def test_dm(db, test_user, other_user):
    """Test DM fixture (ダイレクトメッセージ)"""
    message = Message(
        content="Test DM message",
        sender_id=test_user.id,
        receiver_id=other_user.id
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@pytest.fixture(scope="function")
def get_token(client):
    """Helper fixture to get authentication token for any user"""
    def _get_token(user):
        response = client.post(
            "/auth/token",
            data={
                "username": user.username,
                "password": user.plain_password
            }
        )
        return response.json()["access_token"]
    return _get_token

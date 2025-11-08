import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
from pathlib import Path

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app


@pytest.fixture(scope="function")
def client():
    """FastAPI test client fixture"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def test_db():
    """Test database fixture"""
    # This will be expanded when database integration tests are needed
    pass

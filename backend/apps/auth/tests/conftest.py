# apps/auth/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.sessions import SessionMiddleware
import os
import tempfile

# 테스트용 환경 변수 설정
os.environ["JWT_SECRET"] = "test-secret-key-for-testing"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRE_MINUTES"] = "60"
os.environ["ENVIRONMENT"] = "test"
os.environ["FRONTEND_URL"] = "http://localhost:5173"

# OAuth 테스트용
os.environ["GOOGLE_CLIENT_ID"] = "test-google-client-id"
os.environ["GOOGLE_CLIENT_SECRET"] = "test-google-secret"

# 모델 import
from src.models.database import Base, get_db
from src.models.user import User, OAuthAccount, Image
from src.server import app

# SessionMiddleware 추가
app.add_middleware(SessionMiddleware, secret_key="test-session-secret")

# ⭐ 임시 파일로 SQLite DB 생성
TEST_DB_FILE = tempfile.mktemp(suffix=".db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테이블 생성
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """각 테스트마다 새로운 세션"""
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        # 테이블 데이터 삭제
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture(scope="function")
def client(db):
    """FastAPI TestClient"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    return {
        "user_id": 1,
        "email": "test@example.com",
        "name": "Test User"
    }


@pytest.fixture
def auth_token(mock_user):
    from src.utils.jwt import create_jwt_token
    return create_jwt_token(
        user_id=mock_user["user_id"],
        email=mock_user["email"],
        name=mock_user["name"]
    )


def pytest_sessionfinish(session, exitstatus):
    """테스트 종료 시 DB 파일 삭제"""
    import os
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
# backend/apps/api/tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from moto import mock_s3
import boto3
import os

# ===== 1. 환경 변수 먼저 설정 =====
os.environ["S3_ENDPOINT"] = ""
os.environ["S3_ACCESS_KEY"] = "test-key"
os.environ["S3_SECRET_KEY"] = "test-secret"
os.environ["S3_BUCKET"] = "test-bucket"
os.environ["PUBLIC_S3_BASEURL"] = ""

# ===== 2. Mock을 전역으로 시작 =====
mock = mock_s3()
mock.start()

# ===== 3. 이제 server.py import (mock이 활성화된 상태에서) =====
from src.server import app
from src.config import S3_BUCKET
from src.utils.s3 import s3_internal

from src.models.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile

# ===== 4. Mock S3에 버킷 생성 =====
try:
    s3_internal.create_bucket(Bucket=S3_BUCKET)
except Exception:
    pass

# ✅ 5. 인증 Mock 함수
def mock_get_current_user():
    """테스트용 user_id 반환"""
    return 1

# ✅ 6. 의존성 Override
from src.utils.auth import get_current_user
app.dependency_overrides[get_current_user] = mock_get_current_user


# ✅ 테스트용 SQLite DB
TEST_DB_FILE = tempfile.mktemp(suffix=".db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

test_engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# ✅ 테이블 생성
Base.metadata.create_all(bind=test_engine)

# ✅ DB 의존성 Override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """FastAPI TestClient 생성"""
    return TestClient(app)

@pytest.fixture
def mock_s3_client():
    """Mock S3 클라이언트 (이미 생성된 s3_internal 재사용)"""
    yield s3_internal

# ✅ ✅ ✅ 추가: db fixture 정의
@pytest.fixture(scope="function")
def db():
    """테스트용 DB 세션 (각 테스트마다 초기화)"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # 테스트 후 데이터 정리
        session.rollback()
        
        # 모든 테이블의 데이터 삭제 (테이블은 유지)
        from src.models.image import Image  # Image 모델 import
        session.query(Image).delete()
        session.commit()
        
        session.close()

def pytest_sessionfinish(session, exitstatus):
    """테스트 세션 종료 시 정리"""
    mock.stop()
    app.dependency_overrides.clear()
    
    # ✅ 테스트 DB 파일 삭제
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
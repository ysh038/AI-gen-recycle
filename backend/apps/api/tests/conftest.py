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
from src.server import app, S3_BUCKET, s3_internal

# ===== 4. Mock S3에 버킷 생성 =====
try:
    s3_internal.create_bucket(Bucket=S3_BUCKET)
except Exception:
    pass

@pytest.fixture
def client():
    """FastAPI TestClient 생성"""
    return TestClient(app)

@pytest.fixture
def mock_s3_client():
    """Mock S3 클라이언트 (이미 생성된 s3_internal 재사용)"""
    yield s3_internal

def pytest_sessionfinish(session, exitstatus):
    """테스트 세션 종료 시 mock 정리"""
    mock.stop()
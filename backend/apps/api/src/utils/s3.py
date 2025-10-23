import boto3
import asyncio
from botocore.exceptions import ClientError, EndpointConnectionError
from src.config import (
    S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET,
    PUBLIC_S3_BASEURL, BOTO_CONFIG
)

# 내부용 클라이언트 (서버->MinIO)
s3_internal = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT if S3_ENDPOINT else None,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=BOTO_CONFIG,
    region_name="us-east-1",
)

# 외부용 클라이언트 (presigned 생성 전용)
s3_public = boto3.client(
    "s3",
    endpoint_url=PUBLIC_S3_BASEURL if PUBLIC_S3_BASEURL else None,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=BOTO_CONFIG,
    region_name="us-east-1",
)

def ensure_bucket():
    """버킷 존재 확인 및 생성"""
    try:
        s3_internal.head_bucket(Bucket=S3_BUCKET)
    except ClientError:
        s3_internal.create_bucket(Bucket=S3_BUCKET)

async def wait_for_bucket():
    """MinIO 준비 대기 및 버킷 생성 (재시도 로직 포함)"""
    backoff = 1.0
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            ensure_bucket()
            print(f"✅ Successfully connected to MinIO and ensured bucket '{S3_BUCKET}' exists")
            return
        except EndpointConnectionError as e:
            if attempt < max_retries - 1:
                print(f"⏳ MinIO not ready yet (attempt {attempt + 1}/{max_retries}), retrying in {backoff}s...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 5)
            else:
                raise RuntimeError(f"❌ MinIO is still unavailable after {max_retries} retries") from e
        except Exception as e:
            print(f"⚠️ Unexpected error while connecting to MinIO: {e}")
            raise
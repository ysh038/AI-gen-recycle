# apps/api/src/server.py
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, EndpointConnectionError
import uuid
import os
import urllib.parse
import asyncio

app = FastAPI()

# ===== Env =====
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")  # 내부 통신용
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minio")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minio123")
S3_BUCKET = os.getenv("S3_BUCKET", "uploads")
PUBLIC_S3_BASEURL = os.getenv("PUBLIC_S3_BASEURL", "http://localhost:9000")  # 외부 접근용

cfg = Config(signature_version="s3v4", s3={"addressing_style": "path"})

# 내부용 클라이언트 (서버->MinIO)
s3_internal = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=cfg,
    region_name="us-east-1",
)

# 외부용 클라이언트 (presigned 생성 전용)
s3_public = boto3.client(
    "s3",
    endpoint_url=PUBLIC_S3_BASEURL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=cfg,
    region_name="us-east-1",
)

class UploadRequest(BaseModel):
    filename: str
    contentType: str
    size: int

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/avif"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

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

@app.on_event("startup")
async def on_startup():
    """서버 시작 시 실행"""
    await wait_for_bucket()

@app.post("/uploads")
def create_presigned_put(req: UploadRequest):
    if req.size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    ext = os.path.splitext(req.filename)[1].lower()
    if ext not in ALLOWED_EXT or req.contentType not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # 혼동 방지: 버킷 내부 폴더는 originals/
    object_key = f"originals/{uuid.uuid4().hex}{ext}"

    # NOTE: ContentType을 Params에 넣지 않아 클라이언트 PUT 헤더 미스매치로 인한 서명 실패를 회피
    url = s3_public.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": object_key,
        },
        ExpiresIn=3600,
    )
    return {"presignedUrl": url, "objectKey": object_key}

@app.get("/images/{key:path}")
def create_presigned_get(
    key: str = Path(..., description="오브젝트 키 (예: originals/abc123.jpg)"),
    as_download: bool = Query(False, description="다운로드 강제"),
    filename: str | None = Query(None, description="다운로드 파일명"),
    expires_in: int = Query(900, description="URL 유효시간(초, 60~3600)"),
):
    if key.startswith("/") or ".." in key:
        raise HTTPException(status_code=400, detail="Invalid key")

    try:
        s3_internal.head_object(Bucket=S3_BUCKET, Key=key)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code in ("404", "NoSuchKey", "NotFound"):
            raise HTTPException(status_code=404, detail="Object not found")
        raise

    resp_headers = {}
    if as_download:
        safe = filename or os.path.basename(key) or "download"
        resp_headers["response-content-disposition"] = f"attachment; filename*=UTF-8''{urllib.parse.quote(safe)}"

    # 실제 적용되는 만료 시간 계산 (60~3600초로 클램핑)
    effective_expiry = max(60, min(expires_in, 3600))
    
    url = s3_public.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key, **resp_headers},
        ExpiresIn=effective_expiry,
    )
    
    # 실제 적용된 값을 응답으로 반환
    return {"url": url, "key": key, "expiresIn": effective_expiry, "download": as_download}

# apps/api/src/server.py
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import uuid
import os
import urllib.parse

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
    try:
        s3_internal.head_bucket(Bucket=S3_BUCKET)
    except ClientError:
        s3_internal.create_bucket(Bucket=S3_BUCKET)

ensure_bucket()

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

    url = s3_public.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key, **resp_headers},
        ExpiresIn=max(60, min(expires_in, 3600)),
    )
    return {"url": url, "key": key, "expiresIn": min(expires_in, 3600), "download": as_download}

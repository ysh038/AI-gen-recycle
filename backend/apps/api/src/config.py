import os
from botocore.client import Config

# S3 설정
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minio")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minio123")
S3_BUCKET = os.getenv("S3_BUCKET", "uploads")
PUBLIC_S3_BASEURL = os.getenv("PUBLIC_S3_BASEURL", "http://localhost:9000")

# 업로드 제한
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/avif"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

# Boto3 설정
BOTO_CONFIG = Config(signature_version="s3v4", s3={"addressing_style": "path"})

# CORS 설정
CORS_ORIGINS = [
    "http://localhost:3000",
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]
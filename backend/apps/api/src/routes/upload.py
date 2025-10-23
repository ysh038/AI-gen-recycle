from fastapi import APIRouter, HTTPException
from src.models.schemas import UploadRequest, UploadResponse
from src.utils.s3 import s3_public
from src.config import S3_BUCKET, ALLOWED_EXT, ALLOWED_MIME, MAX_SIZE
import uuid
import os

router = APIRouter()

@router.post("/uploads", response_model=UploadResponse)
def create_presigned_put(req: UploadRequest):
    """Presigned URL 생성 (업로드용)"""
    if req.size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    ext = os.path.splitext(req.filename)[1].lower()
    if ext not in ALLOWED_EXT or req.contentType not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    object_key = f"originals/{uuid.uuid4().hex}{ext}"

    url = s3_public.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": object_key,
        },
        ExpiresIn=3600,
    )
    
    return UploadResponse(presignedUrl=url, objectKey=object_key)
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm.session import Session
from src.models.schemas import UploadRequest, UploadResponse
from src.models.database import get_db
from src.models.image import Image
from src.utils.s3 import s3_public
from src.utils.auth import get_current_user
from src.config import S3_BUCKET, ALLOWED_EXT, ALLOWED_MIME, MAX_SIZE
import uuid
import os

router = APIRouter()

@router.post("/uploads", response_model=UploadResponse)
def create_presigned_put(req: UploadRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
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
     
    # ✅ DB에 메타데이터 저장 (이미 받은 db 사용)
    try:
        image = Image(
            user_id=user_id,
            object_key=object_key,
            filename=req.filename,
            content_type=req.contentType,
            size=req.size
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        print(f"✅ Image saved: ID={image.id}")
    except Exception as e:
        db.rollback()
        print(f"❌ DB Error: {e}")
        raise HTTPException(500, f"Database error: {str(e)}")

    return UploadResponse(presignedUrl=url, objectKey=object_key)
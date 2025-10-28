from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlalchemy.orm.session import Session
from src.models.database import get_db
from src.models.schemas import ImageResponse
from src.utils.s3 import s3_internal, s3_public
from src.config import S3_BUCKET
from botocore.exceptions import ClientError
import urllib.parse
import os
from src.models.image import Image
from src.utils.auth import get_current_user

router = APIRouter()

@router.get("/images/{key:path}", response_model=ImageResponse)
def create_presigned_get(
    key: str = Path(..., description="오브젝트 키 (예: originals/abc123.jpg)"),
    as_download: bool = Query(False, description="다운로드 강제"),
    filename: str | None = Query(None, description="다운로드 파일명"),
    expires_in: int = Query(900, description="URL 유효시간(초, 60~3600)"),
):
    """Presigned URL 생성 (다운로드/조회용)"""
    if key.startswith("/") or ".." in key:
        raise HTTPException(status_code=400, detail="Invalid key")

    # 파일 존재 확인
    try:
        s3_internal.head_object(Bucket=S3_BUCKET, Key=key)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code in ("404", "NoSuchKey", "NotFound"):
            raise HTTPException(status_code=404, detail="Object not found")
        raise

    # 만료 시간 클램핑 (60~3600초)
    effective_expiry = max(60, min(expires_in, 3600))
    
    # Presigned URL 파라미터 구성
    params = {
        "Bucket": S3_BUCKET,
        "Key": key
    }
    
    # 다운로드 모드
    if as_download:
        safe = filename or os.path.basename(key) or "download"
        params["ResponseContentDisposition"] = f"attachment; filename*=UTF-8''{urllib.parse.quote(safe)}"
    
    url = s3_public.generate_presigned_url(
        "get_object",
        Params=params,
        ExpiresIn=effective_expiry,
    )
    
    return ImageResponse(
        url=url,
        key=key,
        expiresIn=effective_expiry,
        download=as_download
    )

@router.get("/images")
async def list_my_images(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """내가 업로드한 이미지 목록"""
    images = db.query(Image)\
        .filter(Image.user_id == user_id)\
        .order_by(Image.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Presigned URL 생성
    result = []
    for img in images:
        url = s3_public.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': img.object_key},
            ExpiresIn=3600
        )
        result.append({
            "id": img.id,
            "key": img.object_key,
            "filename": img.filename,
            "size": img.size,
            "url": url,
            "created_at": img.created_at.isoformat()
        })
    
    return {"images": result, "count": len(result)}
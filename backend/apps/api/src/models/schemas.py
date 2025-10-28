from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UploadRequest(BaseModel):
    filename: str
    contentType: str
    size: int

class UploadResponse(BaseModel):
    presignedUrl: str
    objectKey: str

class ImageResponse(BaseModel):
    url: str
    key: str
    expiresIn: int
    download: bool
    

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None  # ✅ Optional 추가
    avatar_url: Optional[str] = None  # ✅ Optional 추가
    created_at: datetime
    updated_at: datetime
    
    class Config:  # ✅ 추가
        from_attributes = True  # SQLAlchemy 모델에서 변환 허용
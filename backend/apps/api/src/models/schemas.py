from pydantic import BaseModel

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
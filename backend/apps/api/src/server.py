from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.routes import upload, image
from src.utils.s3 import wait_for_bucket
from src.config import CORS_ORIGINS

app = FastAPI(title="Image Upload API")

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 포함
app.include_router(upload.router, tags=["Upload"])
app.include_router(image.router, tags=["Image"])

# 시작 이벤트
@app.on_event("startup")
async def on_startup():
    """서버 시작 시 MinIO 연결 및 버킷 생성"""
    await wait_for_bucket()

# 헬스체크
@app.get("/health")
def health_check():
    return {"status": "ok"}
# apps/auth/src/server.py
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer
from src.utils.jwt import verify_jwt_token
from src.routes import oauth
from starlette.middleware.sessions import SessionMiddleware
import os
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title = "OAuth Service")

# CORS 미들웨어 추가 (SessionMiddleware 전에)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite 개발 서버
        "http://localhost:3000",      # React 개발 서버 (예비)
        "http://localhost:5174",      # Vite 대체 포트
        os.getenv("FRONTEND_URL", "http://localhost:5173"),  # 환경변수
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "change-this-to-a-random-secret-key")
)

app.include_router(oauth.router, prefix="/auth/oauth", tags=["OAuth"])

security = HTTPBearer()

# JWT 검증
@app.post("/auth/verify")
def verify_token(credentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = verify_jwt_token(token)
        return {"user_id": payload["user_id"], "email": payload["email"]}
    except:
        raise HTTPException(401, detail="Invalid token")

# 내 정보 조회
@app.get("/auth/me")
def get_me(credentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt_token(token)

    return {"user_id": payload["user_id"], "email": payload["email"]}

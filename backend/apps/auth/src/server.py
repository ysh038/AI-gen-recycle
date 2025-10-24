# apps/auth/src/server.py
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer
from src.utils.jwt import verify_jwt_token
from src.routes import oauth, auth
from starlette.middleware.sessions import SessionMiddleware
import os
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title = "OAuth Service")

# CORS 미들웨어 추가 (SessionMiddleware 전에)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React 개발 서버
        os.getenv("FRONTEND_URL", "http://localhost:3000"),  # 환경변수
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
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
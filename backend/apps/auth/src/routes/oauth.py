# apps/auth/src/routes/oauth.py
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from starlette.config import Config
from src.utils.oauth_client import oauth, get_google_user_info 
from src.utils.jwt import create_jwt_token
from src.models.user import find_or_create_user
from src.models.database import get_db
import os
from sqlalchemy.orm import Session

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

@router.get("/google")
async def google_login(request: Request):
    """
    Google OAuth 로그인 시작
    브라우저를 Google 로그인 페이지로 리다이렉트
    """
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Google OAuth 콜백"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = await get_google_user_info(token)
        
        # DB에서 사용자 찾기/생성
        user = find_or_create_user(db, user_info)
        
        # JWT 토큰 생성
        jwt_token = create_jwt_token(
            user_id=user.id,  # ⭐ user['user_id'] → user.id
            email=user.email,
            name=user.name
        )
        
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?token={jwt_token}"
        )
        
    except Exception as e:
        raise HTTPException(500, f"OAuth failed: {str(e)}")

# 테스트용
@router.post("/test-token")
def create_test_token(email: str = "test@example.com", db: Session = Depends(get_db)):
    """테스트용 토큰 생성"""
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(403, "Not available in production")
    
    user_info = {
        'provider': 'test',
        'provider_user_id': 'test123',
        'email': email,
        'name': "Test User",
    }
    
    user = find_or_create_user(db, user_info)
    token = create_jwt_token(user.id, user.email, user.name)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user.id,
            "email": user.email,
            "name": user.name
        }
    }
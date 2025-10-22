# apps/auth/src/routes/oauth.py
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from starlette.config import Config
from src.utils.oauth_client import oauth, get_google_user_info 
from src.utils.jwt import create_jwt_token, create_refresh_token, verify_refresh_token
from src.models.user import find_or_create_user, get_user_by_id
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
        
        # ✅ Access Token + Refresh Token 모두 발급
        access_token = create_jwt_token(
            user_id=user.id,
            email=user.email,
            name=user.name
        )
        refresh_token = create_refresh_token(user.id)
        
        # ✅ 두 토큰 모두 URL에 포함
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?token={access_token}&refresh_token={refresh_token}"
        )
        
    except Exception as e:
        raise HTTPException(500, f"OAuth failed: {str(e)}")

@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh Token으로 새로운 Access Token 발급
    
    Request Body:
        {
            "refresh_token": "eyJhbG..."
        }
    
    Returns:
        {
            "access_token": "new_token...",
            "token_type": "bearer"
        }
    """
    try:
        # Refresh Token 검증 및 user_id 추출
        user_id = verify_refresh_token(refresh_token)
        
        # DB에서 사용자 정보 조회
        user = get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(404, "User not found")
        
        # 새로운 Access Token 발급
        new_access_token = create_jwt_token(user.id, user.email, user.name)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(401, f"Invalid refresh token: {str(e)}")


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
    access_token = create_jwt_token(user.id, user.email, user.name)
    refresh_token = create_refresh_token(user.id)  # ✅ 추가
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # ✅ 추가
        "token_type": "bearer",
        "user": {
            "user_id": user.id,
            "email": user.email,
            "name": user.name
        }
    }
# apps/auth/src/utils/jwt.py
from datetime import datetime, timedelta
from typing import Dict, Any
from jose import jwt, JWTError
from fastapi import HTTPException
import os

# 환경 변수
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))  # 기본 24시간

def create_jwt_token(user_id: int, email: str, name: str = None) -> str:
    """
    JWT 토큰 생성
    
    Args:
        user_id: 사용자 ID
        email: 사용자 이메일

    Returns:
        JWT 토큰 문자열
    """
    # 만료 시간 계산
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    
    # 페이로드 구성
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),  # 발급 시간
    }
    
    # 이름이 있으면 추가
    if name:
        payload["name"] = name

    # JWT 생성
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    JWT 토큰 검증
    
    Args:
        token: JWT 토큰 문자열
        
    Returns:
        페이로드 (Dict[str, Any])
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            401, 
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

def create_refresh_token(user_id: int) -> str:
    """
    Refresh 토큰 생성
    
    Args:
        user_id: 사용자 ID
        
    Returns:
        Refresh 토큰 문자열
    """
    expire = datetime.utcnow() + timedelta(days=30)
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_refresh_token(token: str) -> Dict[str, Any]:
    """
    Refresh 토큰 검증
    
    Args:
        token: Refresh 토큰 문자열
        
    Returns:
        페이로드 (Dict[str, Any])
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(401, detail="Invalid token")

        return payload["user_id"]
        
    except JWTError as e:
        raise HTTPException(401, detail=f"Invalid token: {str(e)}")
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from src.utils.jwt import verify_jwt_token

router = APIRouter()
security = HTTPBearer()

@router.post("/verify")
def verify_token(credentials = Depends(security)):
    """JWT 토큰 검증"""
    token = credentials.credentials
    try:
        payload = verify_jwt_token(token)
        return {
            "user_id": payload["user_id"],
            "email": payload["email"]
        }
    except:
        raise HTTPException(401, detail="Invalid token")

@router.get("/me")
def get_me(credentials = Depends(security)):
    """내 정보 조회"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    
    return {
        "user_id": payload["user_id"], 
        "email": payload["email"],
        "name": payload.get("name")  # ✅ name도 포함
    }
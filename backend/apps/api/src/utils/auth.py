from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import httpx
import os

security = HTTPBearer()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8000")

async def get_current_user(credentials = Depends(security)) -> int:
    """
    JWT 토큰에서 user_id 추출
    Auth 서버에 검증 요청
    """
    token = credentials.credentials
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(401, "Invalid token")
            
            data = response.json()
            return data["user_id"]
            
    except httpx.RequestError:
        raise HTTPException(503, "Auth service unavailable")
    except Exception as e:
        raise HTTPException(401, f"Authentication failed: {str(e)}")
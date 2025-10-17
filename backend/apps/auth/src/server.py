# apps/auth/src/server.py
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer
from src.utils.jwt import verify_jwt_token
from src.routes import oauth

app = FastAPI(title = "OAuth Service")

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

from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlalchemy.orm.session import Session
from src.models.database import get_db
from src.models.user import User
from src.models.schemas import UserResponse

router = APIRouter()

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):  # ✅ async 제거
    """사용자 정보 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ✅ from_attributes=True 덕분에 직접 반환 가능
    return user
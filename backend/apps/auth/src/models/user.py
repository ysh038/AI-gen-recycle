# apps/auth/src/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from typing import Optional, Dict
from .database import Base


class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    avatar_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="user", cascade="all, delete-orphan")


class OAuthAccount(Base):
    """OAuth 계정 연결 테이블"""
    __tablename__ = "oauth_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    user = relationship("User", back_populates="oauth_accounts")
    
    # ⭐ Unique constraint 제대로 설정
    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uq_provider_user'),
    )


class Image(Base):
    """이미지 테이블"""
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    object_key = Column(String(500), unique=True, nullable=False, index=True)
    filename = Column(String(500))
    content_type = Column(String(100))
    size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User", back_populates="images")


# ===== CRUD 함수들 =====

def find_or_create_user(db: Session, oauth_info: Dict) -> User:
    """OAuth 정보로 사용자 찾기 또는 생성"""
    provider = oauth_info['provider']
    provider_user_id = oauth_info['provider_user_id']
    
    # 기존 OAuth 계정 찾기
    oauth_account = db.query(OAuthAccount).filter(
        OAuthAccount.provider == provider,
        OAuthAccount.provider_user_id == provider_user_id
    ).first()
    
    if oauth_account:
        return oauth_account.user
    
    # 새 사용자 생성
    user = User(
        email=oauth_info['email'],
        name=oauth_info.get('name'),
        avatar_url=oauth_info.get('avatar_url')
    )
    db.add(user)
    db.flush()
    
    # OAuth 계정 연결
    oauth_account = OAuthAccount(
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_user_id
    )
    db.add(oauth_account)
    db.commit()
    db.refresh(user)
    
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """사용자 ID로 조회"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """이메일로 사용자 조회"""
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    """모든 사용자 목록"""
    return db.query(User).offset(skip).limit(limit).all()


def delete_user(db: Session, user_id: int) -> bool:
    """사용자 삭제"""
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False


def clear_all_users(db: Session):
    """모든 사용자 삭제 (테스트용)"""
    db.query(OAuthAccount).delete()
    db.query(User).delete()
    db.commit()
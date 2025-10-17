# apps/auth/tests/test_jwt.py
import pytest
from src.utils.jwt import create_jwt_token, verify_jwt_token, create_refresh_token, verify_refresh_token
from fastapi import HTTPException

class TestJWT:
    """JWT 유틸리티 테스트"""
    
    def test_create_and_verify_token(self):
        """JWT 토큰 생성 및 검증"""
        user_id = 123
        email = "test@example.com"
        name = "테스트"
        
        # 토큰 생성
        token = create_jwt_token(user_id, email, name)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # 토큰 검증
        payload = verify_jwt_token(token)
        assert payload["user_id"] == user_id
        assert payload["email"] == email
        assert payload.get("name") == name  # ⭐ .get() 사용
        assert "exp" in payload
        assert "iat" in payload
    
    def test_create_token_without_name(self):
        """이름 없이 토큰 생성"""
        user_id = 123
        email = "test@example.com"
        
        # name 없이 생성
        token = create_jwt_token(user_id, email)
        payload = verify_jwt_token(token)
        
        assert payload["user_id"] == user_id
        assert payload["email"] == email
        assert "name" not in payload  # ⭐ name이 없어야 함
    
    def test_verify_invalid_token(self):
        """잘못된 토큰 검증 실패"""
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401
    
    def test_verify_tampered_token(self):
        """변조된 토큰 검증 실패"""
        token = create_jwt_token(1, "test@example.com")
        tampered = token[:-5] + "ABCDE"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(tampered)
        
        assert exc_info.value.status_code == 401
    
    def test_create_refresh_token(self):
        """Refresh 토큰 생성 및 검증"""
        user_id = 456
        email = "test@example.com"
        
        # Refresh 토큰 생성 (user_id만 전달) ⭐
        refresh_token = create_refresh_token(user_id, email)
        assert isinstance(refresh_token, str)
        
        # 검증
        verified_user_id = verify_refresh_token(refresh_token)
        assert verified_user_id == user_id
    
    def test_access_token_as_refresh_token_fails(self):
        """Access 토큰을 Refresh 토큰으로 사용 시 실패"""
        access_token = create_jwt_token(1, "test@example.com")
        
        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token(access_token)
        
        assert exc_info.value.status_code == 401
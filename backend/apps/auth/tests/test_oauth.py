# apps/auth/tests/test_oauth.py
import pytest
from unittest.mock import patch, AsyncMock
from src.models.user import User, OAuthAccount


class TestOAuthRoutes:
    """OAuth 라우트 테스트"""
    
    def test_test_token_endpoint(self, client, db):
        """테스트 토큰 생성 엔드포인트"""
        response = client.post("/auth/oauth/test-token?email=test@example.com")
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
    
    def test_google_login_redirect(self, client):
        """Google 로그인 리다이렉트"""
        # OAuth 리다이렉트는 302 상태 코드 반환
        response = client.get("/auth/oauth/google", follow_redirects=False)
        assert response.status_code in [302, 307]  # 리다이렉트 상태


class TestUserModel:
    """User 모델 테스트"""
    
    def test_find_or_create_user_new(self, db):
        """새 사용자 생성"""
        from src.models.user import find_or_create_user
        
        oauth_info = {
            'provider': 'google',
            'provider_user_id': 'google123',
            'email': 'new@example.com',
            'name': 'New User',
            'avatar_url': 'https://example.com/avatar.jpg'
        }
        
        user = find_or_create_user(db, oauth_info)
        
        assert user.email == 'new@example.com'
        assert user.name == 'New User'
        assert user.id is not None
    
    def test_find_or_create_user_existing(self, db):
        """기존 사용자 찾기"""
        from src.models.user import find_or_create_user
        
        oauth_info = {
            'provider': 'google',
            'provider_user_id': 'google123',
            'email': 'existing@example.com',
            'name': 'Existing User'
        }
        
        # 첫 번째 생성
        user1 = find_or_create_user(db, oauth_info)
        
        # 같은 정보로 다시 호출
        user2 = find_or_create_user(db, oauth_info)
        
        # 같은 사용자여야 함
        assert user1.id == user2.id
        assert user1.email == user2.email

    def test_refresh_token_endpoint(client, db):
        """Refresh Token으로 Access Token 재발급 테스트"""
        # 1. 테스트 토큰 발급
        response = client.post("/auth/oauth/test-token?email=test@example.com")
        assert response.status_code == 200
        
        data = response.json()
        refresh_token = data["refresh_token"]
        
        # 2. Refresh Token으로 새 Access Token 발급
        refresh_response = client.post(
            "/auth/oauth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert refresh_response.status_code == 200
        new_token = refresh_response.json()["access_token"]
        assert new_token is not None
        assert new_token != data["access_token"]  # 다른 토큰이어야 함
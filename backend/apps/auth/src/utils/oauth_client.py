# apps/auth/src/utils/oauth_client.py
import os
from typing import Dict, Optional
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException

# OAuth 설정
oauth = OAuth()

# Google OAuth 설정
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

def get_oauth_client(provider: str):
    """
    OAuth 클라이언트 가져오기
    
    Args:
        provider: 'google' 또는 ''
    
    Returns:
        OAuth 클라이언트
    """
    if provider not in ['google']:
        raise HTTPException(400, f"Unsupported provider: {provider}")

    client = getattr(oauth, provider)
    if not client:
        raise HTTPException(500, f"{provider} OAuth not configured")
    
    return client

async def get_google_user_info(token: Dict) -> Dict:
    """
    Google에서 사용자 정보 가져오기
    
    Args:
        token: OAuth 토큰
    
    Returns:
        사용자 정보 딕셔너리
    """
    client = get_oauth_client('google')
    response = await client.get('https://www.googleapis.com/oauth2/v1/userinfo', token=token)
    response.raise_for_status()
    user_info = response.json()

    return{
        'provider': 'google',
        'provider_user_id': user_info['id'],
        'email': user_info['email'],
        'name': user_info.get('name'),
        'avatar_url': user_info.get('picture'),
    }

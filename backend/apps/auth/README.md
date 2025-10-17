```text
# Auth 서버 (포트 8001) - OAuth만
GET    /auth/oauth/google              # Google 로그인 시작
GET    /auth/oauth/google/callback     # Google 콜백 → JWT 발급
GET    /auth/oauth/github              # GitHub 로그인 시작
GET    /auth/oauth/github/callback     # GitHub 콜백 → JWT 발급

POST   /auth/verify                    # JWT 검증 (다른 서버용)
GET    /auth/me                        # 내 정보 조회
POST   /auth/refresh     
```
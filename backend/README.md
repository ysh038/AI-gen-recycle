# Image Upload MVP

간단한 **이미지 업로드 서버 + OAuth 인증 서버 + S3 호환 스토리지(MinIO)** 아키텍처입니다.  
추후 확장을 고려해 `apps/` 디렉토리 안에 서비스 단위로 추가할 수 있습니다.

---

## 📁 디렉토리 구조

```text
backend/
  ├── docker-compose.yml          # 통합 compose (infra + api + auth)
  ├── .env                        # 환경변수 (prod, local)
  ├── apps/
  │   ├── api/                    # 이미지 업로드 API
  │   │   ├── Dockerfile
  │   │   ├── requirements.txt
  │   │   ├── src/
  │   │   │   └── server.py
  │   │   └── tests/
  │   └── auth/                   # OAuth 인증 서버 ⭐
  │       ├── Dockerfile
  │       ├── requirements.txt
  │       ├── src/
  │       │   ├── server.py
  │       │   ├── routes/
  │       │   │   └── oauth.py
  │       │   ├── models/
  │       │   │   ├── database.py
  │       │   │   └── user.py
  │       │   └── utils/
  │       │       ├── jwt.py
  │       │       └── oauth_client.py
  │       └── tests/
  └── infra/
      ├── db/                     # PostgreSQL 초기화 스크립트
      │   └── init.sql
      └── pgadmin/                # pgAdmin 설정
          └── servers.json
```

---

## ▶️ 실행 명령어 (원하는 것만 켜고/끄는 법)

### 1) 전부 실행 (MinIO + API)
```bash
# 기본 (.env 파일)
docker compose up -d

# 개발 (.env.local)
docker compose --env-file .env.local up -d

# 운영 (.env.prod)
docker compose --env-file .env.prod up -d

#docker compose --profile infra --profile api up -d --build
# docker compose --profile infra --profile api up -d
```

### 2) 인프라만 실행 (MinIO만)
```bash
docker compose --profile infra up -d
```

### 3) API만 실행 (MinIO가 이미 켜져있을 경우)
```bash
docker compose --profile api up -d --build api
```

### 4) API만 재시작 / 재빌드
```bash
# 코드만 수정했을 때
docker compose restart api

# Dockerfile/의존성까지 바뀌었을 때
docker compose build api && docker compose up -d api

# 강제 재생성 (캐시 무시)
docker-compose up -d --force-recreate --build auth
```

### 5) 특정 서비스만 종료
```bash
docker compose stop api
docker compose rm -f api
```

---

## 🔐 Auth 서버 (OAuth + JWT)

Auth 서버는 **Google/GitHub OAuth** 로그인과 **JWT 토큰 발급**을 담당합니다.

### 워크플로우

```markdown
┌─────────────────┐
│ 클라이언트         │
└────┬────────────┘
│ 1. GET /auth/oauth/google
↓
┌─────────────────────────────────┐
│ Auth 서버 (포트 8001)             │
├─────────────────────────────────┤
│ - Google로 리다이렉트              │
│ - OAuth 콜백 처리                 │
│ - DB에 사용자 저장/조회             │
│ - JWT 토큰 생성                   │
└────┬────────────────────┬───────┘
     │                    │
     ↓                    ↓
┌─────────────┐ ┌──────────────┐
│ PostgreSQL  │ │ Google       │
│             │ │ OAuth        │
│ users ●     │ └──────────────┘
│ oauth_accounts ● │
└─────────────┘
```


### 엔드포인트

#### 1) OAuth 로그인 시작
```bash
# Google 로그인 (브라우저에서 접속)
http://localhost:8001/auth/oauth/google

# GitHub 로그인
http://localhost:8001/auth/oauth/github
```

**플로우:**
1. 사용자가 위 URL 접속
2. Google/GitHub 로그인 페이지로 리다이렉트
3. 로그인 완료 후 콜백
4. JWT 토큰 발급
5. 프론트엔드로 리다이렉트 (`http://localhost:5173/auth/callback?token=...`)

#### 2) 테스트 토큰 발급 (개발용)
```bash
# 개발 환경에서만 사용 가능
curl -X POST "http://localhost:8001/auth/oauth/test-token?email=test@example.com"
```

✅ 응답 예시:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "email": "test@example.com",
    "name": "Test User"
  }
}
```

#### 3) JWT 토큰 검증
```bash
curl -X POST "http://localhost:8001/auth/verify" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

✅ 응답 예시:
```json
{
  "user_id": 1,
  "email": "test@example.com"
}
```

#### 4) 내 정보 조회
```bash
curl "http://localhost:8001/auth/me" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

✅ 응답 예시:
```json
{
  "user_id": 1,
  "email": "test@example.com"
}
```

### OAuth 설정

`.env` 파일에 OAuth 클라이언트 정보 추가:

```bash
# JWT
JWT_SECRET=your-secret-key-min-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Google OAuth
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123def456...

# GitHub OAuth (선택)
GITHUB_CLIENT_ID=Iv1.abc123def456...
GITHUB_CLIENT_SECRET=ghp_abc123def456...

# Session (OAuth용)
SESSION_SECRET=random-session-secret-key

# Environment
ENVIRONMENT=development  # production에서는 test-token 비활성화
```

**Google OAuth 설정 방법:**
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 프로젝트 생성
3. OAuth 동의 화면 구성
4. 사용자 인증 정보 → OAuth 클라이언트 ID 생성
5. 승인된 리디렉션 URI: `http://localhost:8001/auth/oauth/google/callback`

---

## 🚀 업로드 과정

이 서버는 **Presigned URL 방식**을 사용합니다.  
즉, API 서버는 파일 자체를 받지 않고 **임시로 유효한 업로드 URL**을 발급해 주며,  
클라이언트(또는 curl)가 해당 URL로 S3/MinIO에 직접 업로드합니다.

---

## 워크플로우

```markdown
┌─────────────────────────────────────────────────────┐
│                   클라이언트                           │
│  (웹/앱)                                             │
└─────┬───────────────────────────────────────────┬───┘
      │                                           │
      │ 1. POST /posts (이미지 업로드 요청)            │ 3. GET /posts/1
      ↓                                           ↓
┌─────────────────────────────────────────────────────┐
│                  API 서버                            │
├─────────────────────────────────────────────────────┤
│  POST /posts:                                       │
│  1. DB에 이미지 메타데이터 저장 (objectKey 포함)            │
   2. 메타데이터 기반으로 presigned URL 생성 및 클라이언트 전달  │
│                                                     │
│  GET /posts/1:                                      │
│    1. DB에서 조회 (objectKey 가져옴)                    │
│    2. objectKey로 presigned URL 생성                  │
│    3. 응답                                            │
└─────┬───────────────────────────────────────┬───────┘
      │                                       │
      │ objectKey: originals/a1b2c3d4.jpg     │
      ↓                                       ↓
┌─────────────────┐               ┌──────────────────┐
│   S3 Storage    │               │   DB (Postgres)  │
│                 │               │                  │
│ a1b2c3d4.jpg ●  │               │ posts:           │
│ f7e8d9c0.png ●  │               │ - id: 1          │
│                 │               │ - image_key: ●   │
└─────────────────┘               └──────────────────┘
       실제 파일                      objectKey (참조)
```

### 1) Presigned URL 발급 (POST /uploads)

```bash
curl -X POST http://localhost:8080/uploads   -H "Content-Type: application/json"   -d '{"filename":"cat.jpg","contentType":"image/jpeg","size":123456}'
```

✅ 성공 시 응답 예시:
```json
{
  "presignedUrl": "http://localhost:9000/uploads/abc123.jpg?...",
  "objectKey": "uploads/abc123.jpg"
}
```

- **검증 로직**
  - 허용 확장자: JPG, PNG, WebP, AVIF (옵션: GIF)
  - 허용 MIME: `image/jpeg`, `image/png`, `image/webp`, `image/avif`
  - 최대 크기: 10MB

- **실패 시**
  - 10MB 초과 → `400 File too large`
  - 확장자/타입 불일치 → `400 Unsupported file type`

---

### 2) Presigned URL로 직접 업로드 (PUT)

```bash
curl -X PUT "<presignedUrl>"   -H "Content-Type: image/jpeg"   --data-binary @cat.jpg
```

- 요청은 API 서버를 거치지 않고 **MinIO(S3)** 로 바로 전송됩니다.
- MinIO 콘솔(<http://localhost:9001>)에서 `uploads/` 버킷 안에 업로드된 객체를 확인할 수 있습니다.

---

### 3) 조회 Presigned URL 발급 (GET /images/:key) [선택]

```bash
curl "http://localhost:8080/images/uploads/abc123.jpg"
```

✅ 성공 시 응답 예시:
```json
{
  "url": "http://localhost:9000/uploads/abc123.jpg?...",
  "key": "uploads/abc123.jpg",
  "expiresIn": 900,
  "download": false
}
```

- `as_download=true&filename=cat.jpg` 옵션으로 다운로드 강제 가능:
```bash
curl "http://localhost:8080/images/uploads/abc123.jpg?as_download=true&filename=cat.jpg"
```

## 테스트

기본적으로 git push 실행 시 Github Action을 통해 api Dockerfile 테스트 진행

### test_upload.sh를 통한 테스트

1. brew install jq 등으로 jq 설치
2. chmod +x test_upload.sh
3. ./test_upload.sh

### pytest를 통한 테스트

1. (api 테스트의 경우) pytest /apps/api/tests

2. (auth 테스트의 경우) pytest /apps/auth/tests

### 일회용 컨테이너 환경에서 테스트

1. docker compose --profile test run --rm api-test
2. docker compose --profile test run --rm auth-test

### MinIO 콘솔에서 확인

1. [MinIO 콘솔](http://localhost:9001) 접속
2. 로그인(minio / minio123) 
3. uploads 버킷에서 이미지 확인

### pgadmin에서 DB 확인

1. [pgadmin 콘솔](http://localhost:5050/browser/) 접속
2. 비밀번호 입력 (초기 비밀번호 postgres)
3. Server -> Databases -> recycle_db -> Schemas -> Tables

---

## 🔑 업로드 과정 요약

1. 클라이언트가 **API 서버에 업로드 요청** → Presigned PUT URL 발급
2. 클라이언트가 **Presigned URL로 직접 PUT 업로드** → MinIO에 저장
3. 필요 시 **조회용 Presigned GET URL 발급** → 제한 시간 동안만 다운로드 가능

---

## 🏗️ 서비스 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| **API 서버** | 8080 | 이미지 업로드/다운로드 |
| **Auth 서버** | 8001 | OAuth 인증, JWT 발급 |
| MinIO (S3) | 9000 | 객체 스토리지 |
| MinIO Console | 9001 | MinIO 관리 UI |
| PostgreSQL | 5432 | 사용자/메타데이터 DB |
| pgAdmin | 5050 | DB 관리 UI |

---

## 🔗 참고
- **MinIO Console**: <http://localhost:9001>  
- **API 서버**: <http://localhost:8080>  
- 기본 MinIO 계정: `minio / minio123`

---

## To-Do

- Redis
- CloudFlare
- Jenkins 등 CI/CD / GitHub Action을 통한 CI/CD / commit message 자동화?
- S3 전환
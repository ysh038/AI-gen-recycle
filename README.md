# AI-gen-recycle

이미지 업로드/다운로드 플랫폼 with OAuth 인증

---

## 📋 프로젝트 개요

- **Frontend**: React + TypeScript + Vite (OAuth 로그인, 이미지 업로드 UI)
- **Backend**: FastAPI 마이크로서비스 아키텍처
  - **API 서버** (8080): 이미지 업로드/다운로드 (Presigned URL)
  - **Auth 서버** (8001): OAuth 2.0 인증 (Google, GitHub)
- **Storage**: MinIO (S3 호환)
- **Database**: PostgreSQL
- **Containerization**: Docker + Docker Compose

---

## 🚀 빠른 시작

### 1) 전체 서비스 실행 (Docker Compose)

```bash
cd backend

# 환경 변수 설정 (.env 파일 생성)
cp .env.example .env

# 모든 서비스 시작 (MinIO, PostgreSQL, API, Auth)
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

**서비스 URL:**
- Frontend: http://localhost:5173
- API 서버: http://localhost:8080
- Auth 서버: http://localhost:8001
- MinIO Console: http://localhost:9001
- pgAdmin: http://localhost:5050

### 2) 프론트엔드 개발 서버

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 시작
npm run dev
```

### 3) 테스트

```bash
# Backend 테스트
cd backend
docker-compose --profile test up --abort-on-container-exit

# Frontend 테스트
cd frontend
npm test
```

---

## 📁 프로젝트 구조

```text
AI-gen-recycle/
├── frontend/                  # React 프론트엔드
│   ├── src/
│   │   ├── routes/           # 페이지 (Login, AuthCallback, Home)
│   │   ├── queries/          # React Query (API 호출)
│   │   ├── stores/           # Zustand (Auth 상태 관리)
│   │   └── App.tsx
│   ├── .env                  # 환경 변수
│   ├── package.json
│   └── README.md             # 📘 프론트엔드 상세 문서
│
├── backend/
│   ├── apps/
│   │   ├── api/              # API 서버 (이미지 업로드/다운로드)
│   │   │   ├── src/
│   │   │   │   └── server.py
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   └── requirements.txt
│   │   │
│   │   └── auth/             # Auth 서버 (OAuth 인증)
│   │       ├── src/
│   │       │   ├── server.py
│   │       │   ├── routes/oauth.py
│   │       │   ├── models/   # SQLAlchemy ORM
│   │       │   └── utils/    # JWT, OAuth Client
│   │       ├── tests/
│   │       ├── Dockerfile
│   │       └── requirements.txt
│   │
│   ├── infra/
│   │   ├── db/init.sql       # PostgreSQL 초기화
│   │   └── pgadmin/servers.json
│   │
│   ├── docker-compose.yml    # 전체 서비스 오케스트레이션
│   ├── test_upload.sh        # 통합 테스트 스크립트
│   └── README.md             # 📘 백엔드 상세 문서
│
├── .github/
│   └── workflows/
│       └── test.yml          # GitHub Actions CI/CD
│
└── README.md                 # 📘 이 파일 (전체 개요)
```

---

## 🔑 OAuth 로그인 설정

### 1) Google OAuth

1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. **APIs & Services** → **Credentials** → **Create OAuth 2.0 Client ID**
3. **Authorized redirect URIs**:
   ```
   http://localhost:8001/auth/oauth/google/callback
   ```
4. 발급된 `Client ID`와 `Client Secret`을 `.env`에 추가:
   ```bash
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

### 2) GitHub OAuth

1. [GitHub Settings](https://github.com/settings/developers) → **OAuth Apps** → **New OAuth App**
2. **Authorization callback URL**:
   ```
   http://localhost:8001/auth/oauth/github/callback
   ```
3. 발급된 `Client ID`와 `Client Secret`을 `.env`에 추가:
   ```bash
   GITHUB_CLIENT_ID=your-github-client-id
   GITHUB_CLIENT_SECRET=your-github-client-secret
   ```

---

## 📚 상세 문서

- **Frontend**: [frontend/README.md](frontend/README.md)
- **Backend**: [backend/README.md](backend/README.md)
- **API 서버**: [backend/apps/api/README.md](backend/apps/api/README.md)
- **Auth 서버**: [backend/apps/auth/README.md](backend/apps/auth/README.md)

---

## 🚀 배포

---

## 📝 To-Do

- [ ] 이미지 목록 조회 API
- [ ] 이미지 삭제 API (본인만)
- [ ] 프로필 페이지
- [ ] Redis (Job Queue)
- [ ] CloudFlare CDN 연동
- [ ] AWS S3 전환 (MinIO → S3)

---

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

MIT License

---

## 👤 Contact

- **GitHub**: [@ysh038](https://github.com/ysh038)
- **Email**: youje12345@gmail.com
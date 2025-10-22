# AI-gen-recycle Frontend

**React + TypeScript + Vite** 기반의 OAuth 로그인을 지원하는 이미지 업로드 프론트엔드입니다.

---

## 📁 디렉토리 구조

```text
frontend/
  ├── src/
  │   ├── App.tsx                    # 메인 App 컴포넌트 + 라우팅
  │   ├── main.tsx                   # 엔트리포인트
  │   ├── routes/                    # 페이지 컴포넌트
  │   │   ├── Home/
  │   │   │   ├── Home.tsx
  │   │   │   └── Home.module.css
  │   │   ├── Login/                 # OAuth 로그인 페이지 ⭐
  │   │   │   ├── Login.tsx
  │   │   │   └── Login.module.css
  │   │   ├── AuthCallback/          # OAuth 콜백 페이지 ⭐
  │   │   │   └── AuthCallback.tsx
  │   │   └── index.ts
  │   ├── queries/                   # React Query hooks
  │   │   └── login/                 # OAuth 로그인 로직 ⭐
  │   │       ├── login.ts           # API 함수들
  │   │       └── index.ts           # React Query hooks
  │   ├── stores/                    # Zustand 상태 관리
  │   │   └── shared/
  │   │       └── index.ts           # Auth store (토큰, 사용자) ⭐
  │   ├── components/                # 재사용 컴포넌트
  │   ├── hooks/                     # 커스텀 hooks
  │   ├── utils/                     # 유틸리티 함수
  │   └── types/                     # TypeScript 타입 정의
  ├── .env                           # 환경 변수
  ├── package.json
  ├── vite.config.ts
  └── tsconfig.json
```

---

## 🛠️ 기술 스택

| 카테고리 | 기술 |
|---------|------|
| **프레임워크** | React 19.1.0 |
| **언어** | TypeScript 5.8.3 |
| **빌드 도구** | Vite 6.3.5 |
| **라우팅** | React Router DOM 7.6.0 |
| **상태 관리** | Zustand 5.0.4 (토큰, 사용자) |
| **서버 상태** | TanStack React Query 5.75.7 |
| **스타일링** | CSS Modules |

---

## 🚀 실행 방법

### 1) 개발 서버 시작

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행 (http://localhost:5173)
npm run dev
```

### 2) 프로덕션 빌드

```bash
# 빌드
npm run build

# 빌드 결과 미리보기
npm run preview
```

### 3) 코드 품질

```bash
# ESLint 실행
npm run lint

# ESLint 자동 수정
npm run lint:fix

# Prettier 포맷팅
npm run prettier:fix
```

---

## 🔐 OAuth 로그인 플로우

### 전체 흐름도

```
┌────────────────────────────────────────────────────────────┐
│                    사용자 브라우저                           │
└────┬──────────────────────────────────────────────┬────────┘
     │                                               │
     │ 1. /login 접속                                │ 7. /auth/callback?token=xxx
     │                                               │
┌────▼───────────────────────────────────────────────▼────────┐
│              React App (localhost:5173)                     │
├─────────────────────────────────────────────────────────────┤
│  Login 페이지                    AuthCallback 페이지         │
│  - "Google로 로그인" 버튼          - URL에서 토큰 추출        │
│  - 클릭 시 리다이렉트              - Zustand에 토큰 저장      │
│                                  - 사용자 정보 조회         │
│                                  - 홈으로 리다이렉트         │
└────┬────────────────────────────────────────────────────────┘
     │
     │ 2. window.location.href = "/auth/oauth/google"
     ↓
┌─────────────────────────────────────────────────────────────┐
│          Auth 서버 (localhost:8001)                          │
├─────────────────────────────────────────────────────────────┤
│  3. Google로 리다이렉트                                       │
│  4. 콜백 처리 (/auth/oauth/google/callback)                 │
│  5. DB에 사용자 저장                                         │
│  6. JWT 토큰 생성                                            │
│  7. 프론트엔드로 리다이렉트 (token 포함)                      │
└────┬────────────────────────────────────────────────────────┘
     │
     │ 3-6. Google OAuth
     ↓
┌─────────────────────────────────────────────────────────────┐
│                  Google OAuth                                │
│  - 사용자 로그인                                              │
│  - 권한 승인                                                 │
│  - Auth 서버로 콜백                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 주요 파일 설명

### 1. `src/queries/login/login.ts` - OAuth API 함수

```typescript
/**
 * Google OAuth 로그인 시작
 */
export const initiateGoogleLogin = () => {
  window.location.href = `${AUTH_API_BASE}/auth/oauth/google`;
};

/**
 * JWT 토큰 검증
 */
export const verifyToken = async (token: string) => {
  const response = await fetch(`${AUTH_API_BASE}/auth/verify`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return response.json();
};

/**
 * 내 정보 조회
 */
export const getMe = async (token: string) => {
  const response = await fetch(`${AUTH_API_BASE}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return response.json();
};
```

---

### 2. `src/queries/login/index.ts` - React Query Hooks

```typescript
/**
 * 사용자 정보 조회 훅
 * - JWT 토큰으로 사용자 정보 가져오기
 * - React Query로 캐싱
 */
export const useGetMe = (token: string | null, enabled = true) => {
  return useQuery({
    queryKey: ['user', 'me', token],
    queryFn: () => getMe(token!),
    enabled: enabled && !!token,
    staleTime: 1000 * 60 * 5, // 5분 캐싱
  });
};

/**
 * 테스트 토큰 발급 훅 (개발용)
 */
export const useGetTestToken = () => {
  return useMutation({
    mutationFn: (email?: string) => getTestToken(email),
    onSuccess: (data) => {
      // 토큰 자동 저장
    },
  });
};
```

---

### 3. `src/stores/shared/index.ts` - Auth Store (Zustand)

```typescript
interface AuthState {
  token: string | null;           // JWT 토큰
  user: User | null;              // 사용자 정보
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

/**
 * 인증 상태 관리 (Zustand + localStorage)
 * - JWT 토큰 저장
 * - 사용자 정보 저장
 * - 자동 로그인 (localStorage persist)
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      setToken: (token) => set({ token }),
      setUser: (user) => set({ user }),
      logout: () => set({ token: null, user: null }),
      isAuthenticated: () => !!get().token,
    }),
    {
      name: 'auth-storage', // localStorage 키
    }
  )
);
```

---

### 4. `src/routes/Login/Login.tsx` - 로그인 페이지

```typescript
/**
 * 로그인 페이지
 * - Google OAuth 로그인 버튼
 * - GitHub OAuth 로그인 버튼
 * - 테스트 로그인 (개발 모드만)
 */
function Login() {
  const handleGoogleLogin = () => {
    initiateGoogleLogin(); // Auth 서버로 리다이렉트
  };

  return (
    <main>
      <h1>로그인</h1>
      <button onClick={handleGoogleLogin}>
        🔐 Google로 로그인
      </button>
    </main>
  );
}
```

---

### 5. `src/routes/AuthCallback/AuthCallback.tsx` - OAuth 콜백 페이지

```typescript
/**
 * OAuth 콜백 페이지
 * - URL에서 JWT 토큰 추출
 * - Zustand에 저장
 * - 사용자 정보 조회
 * - 홈으로 리다이렉트
 */
function AuthCallback() {
  useEffect(() => {
    const token = extractTokenFromUrl();
    if (token) {
      setToken(token);
    }
  }, []);

  const { data: userData } = useGetMe(token);

  useEffect(() => {
    if (userData) {
      setUser(userData);
      navigate('/'); // 홈으로 이동
    }
  }, [userData]);

  return <div>로그인 중...</div>;
}
```

---

### 6. `src/App.tsx` - 라우팅 + 인증 보호

```typescript
/**
 * 메인 App 컴포넌트
 * - 라우팅 설정
 * - 인증 보호 (Private Routes)
 */
function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());

  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path="/" 
          element={isAuthenticated ? <Home /> : <Navigate to="/login" />} 
        />
        <Route path="/login" element={<Login />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🌐 환경 변수

`.env` 파일:

```bash
# Auth 서버 URL
VITE_AUTH_API_BASE=http://localhost:8001

# API 서버 URL (이미지 업로드)
VITE_API_BASE=http://localhost:8080
```

**사용 예시:**
```typescript
const AUTH_API_BASE = import.meta.env.VITE_AUTH_API_BASE;
```

---

## 🧪 개발 팁

### 1) 테스트 로그인 사용

개발 중 Google OAuth 설정 없이 테스트:

```typescript
// Login.tsx에서
{import.meta.env.DEV && (
  <button onClick={handleTestLogin}>
    🧪 테스트 로그인
  </button>
)}
```

### 2) React Query DevTools

개발 서버에서 자동 활성화:
- 브라우저 우하단에 React Query 아이콘 표시
- 쿼리 상태, 캐시 확인 가능

### 3) localStorage 확인

```javascript
// 브라우저 콘솔에서
localStorage.getItem('auth-storage')
// → {"token": "eyJhbG...", "user": {...}}
```

### 4) 토큰 만료 시 자동 로그아웃

```typescript
// queries/login/login.ts
export const getMe = async (token: string) => {
  const response = await fetch(`${AUTH_API_BASE}/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });

  if (response.status === 401) {
    // 토큰 만료
    useAuthStore.getState().logout();
    window.location.href = '/login';
  }

  return response.json();
};
```

---

## 🔗 API 엔드포인트

### Auth 서버 (localhost:8001)

| 엔드포인트 | 메서드 | 설명 |
|-----------|-------|------|
| `/auth/oauth/google` | GET | Google OAuth 시작 (리다이렉트) |
| `/auth/oauth/github` | GET | GitHub OAuth 시작 (리다이렉트) |
| `/auth/oauth/google/callback` | GET | Google OAuth 콜백 (서버 전용) |
| `/auth/oauth/test-token` | POST | 테스트 토큰 발급 (개발용) |
| `/auth/verify` | POST | JWT 토큰 검증 |
| `/auth/me` | GET | 내 정보 조회 (JWT 필요) |

### API 서버 (localhost:8080)

| 엔드포인트 | 메서드 | 설명 |
|-----------|-------|------|
| `/uploads` | POST | Presigned URL 발급 |
| `/images/:key` | GET | 조회용 Presigned URL 발급 |

---

## 🐛 트러블슈팅

### 1. CORS 에러

```
Access to XMLHttpRequest has been blocked by CORS policy
```

**해결:** Auth 서버에 CORS 미들웨어 추가 확인
```python
# backend/apps/auth/src/server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 토큰이 저장되지 않음

**확인 사항:**
- AuthCallback 컴포넌트가 `/auth/callback` 경로에 매핑되어 있는지
- URL에 `?token=xxx` 파라미터가 있는지
- localStorage에 저장되는지 (브라우저 콘솔에서 확인)

### 3. 로그인 후 홈으로 리다이렉트 안 됨

**확인 사항:**
- `useGetMe` 훅이 정상 작동하는지
- `userData`가 제대로 받아와지는지
- `navigate('/')` 호출되는지

### 4. Google OAuth 설정 에러

```
redirect_uri_mismatch
```

**해결:** Google Cloud Console에서 리다이렉트 URI 확인
```
등록된 URI: http://localhost:8001/auth/oauth/google/callback
실제 요청 URI: http://localhost:8001/auth/oauth/google/callback
→ 정확히 일치해야 함 (슬래시 주의!)
```

---

## 📦 의존성

### 주요 라이브러리

```json
{
  "dependencies": {
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "react-router-dom": "^7.6.0",
    "@tanstack/react-query": "^5.75.7",
    "zustand": "^5.0.4"
  },
  "devDependencies": {
    "vite": "^6.3.5",
    "typescript": "~5.8.3",
    "@types/react": "^19.1.2"
  }
}
```

---

## 🚀 배포

### Vercel 배포

```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
vercel

# 환경 변수 설정
vercel env add VITE_AUTH_API_BASE
vercel env add VITE_API_BASE
```

### Netlify 배포

```bash
# Netlify CLI 설치
npm i -g netlify-cli

# 배포
netlify deploy --prod

# 환경 변수는 Netlify 대시보드에서 설정
```

---

## 📚 참고 링크

- **Backend README**: [../backend/README.md](../backend/README.md)
- **React Router**: https://reactrouter.com
- **TanStack Query**: https://tanstack.com/query
- **Zustand**: https://zustand-demo.pmnd.rs
- **Vite**: https://vitejs.dev

---

## 📝 To-Do

- [ ] 프로필 페이지 추가
- [ ] 로그아웃 버튼 추가
- [ ] 이미지 업로드 UI 구현
- [ ] 이미지 갤러리 페이지
- [ ] 토큰 자동 갱신 (Refresh Token)
- [ ] 에러 바운더리 추가
- [ ] 로딩 스피너 컴포넌트
- [ ] 테스트 코드 추가 (cypress)

# AI-gen-recycle Frontend (Next.js)

**Next.js 15 + TypeScript** 기반의 OAuth 로그인을 지원하는 이미지 업로드 프론트엔드입니다.

> ⚠️ **Migration Notice**: Vite + React에서 Next.js로 마이그레이션되었습니다. (SEO 최적화)

---

## 📁 디렉토리 구조

```text
frontend-migration/
  ├── app/                          # Next.js App Router
  │   ├── layout.tsx                # 루트 레이아웃
  │   ├── page.tsx                  # 홈 페이지
  │   ├── providers.tsx             # React Query Provider ⭐
  │   ├── login/
  │   │   └── page.tsx              # 로그인 페이지 ⭐
  │   ├── auth/
  │   │   └── callback/
  │   │       └── page.tsx          # OAuth 콜백 페이지 ⭐
  │   └── gallery/
  │       └── page.tsx              # 이미지 갤러리
  ├── components/                   # 재사용 컴포넌트
  │   └── home/
  │       └── Images.tsx            # 이미지 목록 컴포넌트
  ├── queries/                      # React Query hooks
  │   ├── login/                    # OAuth 로그인 로직 ⭐
  │   │   ├── login.ts              # API 함수들
  │   │   ├── axios-config.ts       # Axios 인터셉터 (토큰 갱신)
  │   │   └── index.ts              # React Query hooks
  │   └── image/                    # 이미지 관련 API
  │       ├── image.ts
  │       └── index.ts
  ├── stores/                       # Zustand 상태 관리
  │   └── shared/
  │       └── user.ts               # Auth store (토큰, 사용자) ⭐
  ├── types/                        # TypeScript 타입 정의
  │   └── shared/
  │       ├── user.ts
  │       └── index.ts
  ├── .env                          # 환경 변수
  ├── next.config.ts                # Next.js 설정
  ├── package.json
  └── tsconfig.json
```

---

## 🛠️ 기술 스택

| 카테고리 | 기술 |
|---------|------|
| **프레임워크** | Next.js 15.1.6 |
| **언어** | TypeScript 5.x |
| **라우팅** | Next.js App Router (SSR/SSG) ⭐ |
| **상태 관리** | Zustand 5.0.4 (토큰, 사용자) |
| **서버 상태** | TanStack React Query 5.x |
| **HTTP 클라이언트** | Axios (토큰 갱신 인터셉터) ⭐ |
| **스타일링** | Tailwind CSS + CSS Modules |

---

## 🚀 실행 방법

### 1) 개발 서버 시작

```bash
cd frontend-migration

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

→ `http://localhost:3000` 접속

### 2) 프로덕션 빌드

```bash
# 빌드
npm run build

# 프로덕션 서버 실행
npm start
```

### 3) 코드 품질

```bash
# ESLint 실행
npm run lint

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
     │ 1. /login 접속                                │ 7. /auth/callback?token=xxx&refresh_token=yyy
     │                                               │
┌────▼───────────────────────────────────────────────▼────────┐
│           Next.js App (localhost:3000) ⭐                    │
├─────────────────────────────────────────────────────────────┤
│  Login 페이지 (Client)          AuthCallback 페이지 (Client) │
│  - "Google로 로그인" 버튼          - URL에서 토큰 추출        │
│  - 클릭 시 리다이렉트              - Zustand에 토큰 저장      │
│  - 테스트 로그인 (dev only)       - 사용자 정보 조회         │
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
│  6. JWT Access Token + Refresh Token 생성 ⭐                │
│  7. 프론트엔드로 리다이렉트 (두 토큰 포함)                    │
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

### 1. `app/providers.tsx` - React Query Provider ⭐

```typescript
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

/**
 * React Query Provider (Client Component)
 * - Server Component에서 QueryClient를 직접 생성하면 에러 발생
 * - useState로 Client에서 생성
 */
export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

---

### 2. `queries/login/axios-config.ts` - Axios 인터셉터 (토큰 갱신) ⭐

```typescript
import axios from 'axios'
import { useAuthStore } from '@/stores/shared/user'
import { refreshAccessToken } from './login'

const AUTH_API_BASE = process.env.NEXT_PUBLIC_AUTH_API_BASE || 'http://localhost:8001'

export const authAxios = axios.create({
  baseURL: AUTH_API_BASE,
})

/**
 * Request 인터셉터: Access Token 자동 추가
 */
authAxios.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Response 인터셉터: 401 시 Refresh Token으로 재시도
 */
authAxios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = useAuthStore.getState().refreshToken

      if (refreshToken) {
        try {
          const newAccessToken = await refreshAccessToken(refreshToken)
          useAuthStore.getState().setToken(newAccessToken)

          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return authAxios(originalRequest)
        } catch (refreshError) {
          useAuthStore.getState().logout()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      }
    }

    return Promise.reject(error)
  }
)
```

---

### 3. `queries/login/login.ts` - OAuth API 함수

```typescript
import axios from 'axios'
import { authAxios } from './axios-config'

const AUTH_API_BASE = process.env.NEXT_PUBLIC_AUTH_API_BASE || 'http://localhost:8001'

/**
 * Google OAuth 로그인 시작
 */
export const initiateGoogleLogin = () => {
  window.location.href = `${AUTH_API_BASE}/auth/oauth/google`
}

/**
 * URL에서 Access Token + Refresh Token 추출
 */
export const extractTokensFromUrl = (): {
  token: string | null
  refreshToken: string | null
} => {
  const params = new URLSearchParams(window.location.search)
  return {
    token: params.get('token'),
    refreshToken: params.get('refresh_token'),
  }
}

/**
 * Refresh Token으로 Access Token 재발급 ⭐
 */
export const refreshAccessToken = async (refreshToken: string): Promise<string> => {
  const response = await axios.post(`${AUTH_API_BASE}/auth/oauth/refresh`, {
    refresh_token: refreshToken,
  })

  if (response.status !== 200) {
    throw new Error('Token refresh failed')
  }

  return response.data.access_token
}

/**
 * JWT 토큰 검증
 */
export const verifyToken = async (token: string) => {
  const response = await authAxios.post('/auth/verify')
  return response.data
}

/**
 * 내 정보 조회
 */
export const getMe = async (token: string) => {
  const response = await authAxios.get('/auth/me')
  return response.data
}

/**
 * 테스트 토큰 발급 (개발용)
 */
export const getTestToken = async (email: string = 'test@example.com') => {
  const response = await axios.post(`${AUTH_API_BASE}/auth/oauth/test-token`, { email })

  if (response.status !== 200) {
    throw new Error('Failed to get test token')
  }

  return response.data
}
```

---

### 4. `stores/shared/user.ts` - Auth Store (Zustand + Persist) ⭐

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface IUser {
  user_id: number
  email: string
  name?: string
}

interface IAuthState {
  token: string | null
  refreshToken: string | null  // ⭐ Refresh Token 추가
  user: IUser | null
  setToken: (token: string | null) => void
  setRefreshToken: (refreshToken: string | null) => void  // ⭐
  setUser: (user: IUser | null) => void
  logout: () => void
  isAuthenticated: () => boolean
}

/**
 * 인증 상태 관리
 * - localStorage에 자동 저장 (새로고침 시 로그인 유지)
 * - Access Token + Refresh Token 관리
 */
export const useAuthStore = create<IAuthState>()(
  persist(
    (set, get) => ({
      token: null,
      refreshToken: null,
      user: null,
      setToken: (token) => set({ token }),
      setRefreshToken: (refreshToken) => set({ refreshToken }),
      setUser: (user) => set({ user }),
      logout: () => set({ token: null, refreshToken: null, user: null }),
      isAuthenticated: () => {
        const { token } = get()
        return !!token
      },
    }),
    {
      name: 'auth-storage',  // localStorage 키
    }
  )
)
```

---

### 5. `app/login/page.tsx` - 로그인 페이지

```typescript
'use client'  // ⭐ Client Component

import { useRouter } from 'next/navigation'  // ⭐ next/navigation
import { useGetTestToken, initiateGoogleLogin } from '@/queries/login'

/**
 * 로그인 페이지
 * - Google OAuth 로그인 버튼
 * - 테스트 로그인 (개발 모드만)
 */
function Login() {
  const testTokenMutation = useGetTestToken()
  const router = useRouter()

  const handleGoogleLogin = () => {
    initiateGoogleLogin()  // Auth 서버로 리다이렉트
  }

  const handleTestLogin = () => {
    testTokenMutation.mutate('test@example.com', {
      onSuccess: () => {
        console.log('✅ Test login success')
        router.push('/')  // ⭐ Next.js router
      },
    })
  }

  return (
    <main>
      <h1>로그인</h1>
      
      <button onClick={handleGoogleLogin}>
        🔐 Google로 로그인
      </button>

      {/* 개발 환경에서만 표시 */}
      {process.env.NODE_ENV === 'development' && (  // ⭐ process.env
        <button
          onClick={handleTestLogin}
          disabled={testTokenMutation.isPending}
        >
          {testTokenMutation.isPending ? '로딩중...' : '🧪 테스트 로그인'}
        </button>
      )}
    </main>
  )
}

export default Login
```

---

### 6. `app/auth/callback/page.tsx` - OAuth 콜백 페이지

```typescript
'use client'  // ⭐ Client Component

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'  // ⭐ next/navigation
import { extractTokensFromUrl } from '@/queries/login'
import { useAuthStore } from '@/stores/shared/user'
import { useGetMe } from '@/queries/login'

/**
 * OAuth 콜백 페이지
 * - URL에서 Access Token + Refresh Token 추출
 * - Zustand에 저장
 * - 사용자 정보 조회
 * - 홈으로 리다이렉트
 */
function AuthCallback() {
  const router = useRouter()
  const { setToken, setRefreshToken, setUser, token } = useAuthStore()

  useEffect(() => {
    const { token: urlToken, refreshToken } = extractTokensFromUrl()
    
    console.log('🔍 Extracted from URL:', { 
      token: urlToken ? 'exists' : 'null',
      refreshToken: refreshToken ? 'exists' : 'null' 
    })
    
    if (urlToken && refreshToken) {
      setToken(urlToken)
      setRefreshToken(refreshToken)  // ⭐ Refresh Token 저장
      console.log('✅ Tokens saved to store')
      
      // URL 정리
      window.history.replaceState({}, '', '/auth/callback')
    } else if (!token) {
      console.error('❌ No tokens in URL and store')
      router.push('/login')
    }
  }, [])

  const { data: userData, isLoading, error } = useGetMe(token, !!token)

  useEffect(() => {
    if (userData) {
      setUser(userData)
      console.log('✅ User info loaded:', userData)
      router.push('/')
    }
  }, [userData, setUser, router])

  useEffect(() => {
    if (error) {
      console.error('❌ Failed to fetch user info:', error)
      router.push('/login')
    }
  }, [error, router])

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      {isLoading ? (
        <>
          <h2>로그인 중...</h2>
          <p>잠시만 기다려주세요.</p>
        </>
      ) : (
        <h2>사용자 정보 로딩 중...</h2>
      )}
    </div>
  )
}

export default AuthCallback
```

---

### 7. `app/gallery/page.tsx` - 이미지 갤러리

```typescript
'use client'  // ⭐ Client Component

import { useMyImages } from '@/queries/image'

/**
 * 이미지 갤러리 페이지
 * - 내가 업로드한 이미지 목록 표시
 * - Presigned URL로 이미지 로드
 */
export default function GalleryPage() {
  const { data, isLoading, error } = useMyImages()
  
  if (isLoading) {
    return <div>이미지 로딩 중...</div>
  }
  
  if (error) {
    return <div>에러 발생: {error instanceof Error ? error.message : '알 수 없는 오류'}</div>
  }
  
  if (!data || data.images.length === 0) {
    return <div>업로드한 이미지가 없습니다.</div>
  }
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">내 이미지</h1>
      
      <div className="text-sm text-gray-500 mb-4">
        총 {data.count}개의 이미지
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {data.images.map((image) => (
          <div key={image.id} className="border rounded-lg overflow-hidden shadow">
            {/* ⚠️ Next.js Image 대신 일반 img 사용 (Presigned URL) */}
            <img 
              src={image.url}
              alt={image.filename}
              className="w-full h-48 object-cover"
              loading="lazy"
            />
            
            <div className="p-3">
              <p className="text-sm font-medium truncate">{image.filename}</p>
              <p className="text-xs text-gray-500">{formatFileSize(image.size)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
```

---

## 🌐 환경 변수

`.env` 파일:

```bash
# Auth 서버 URL
NEXT_PUBLIC_AUTH_API_BASE=http://localhost:8001

# API 서버 URL (이미지 업로드)
NEXT_PUBLIC_API_BASE=http://localhost:8080
```

⚠️ **주의:** Next.js에서는 `NEXT_PUBLIC_` 접두사가 필요합니다!

---

## 🔗 API 엔드포인트

### Auth 서버 (localhost:8001)

| 엔드포인트 | 메서드 | 설명 |
|-----------|-------|------|
| `/auth/oauth/google` | GET | Google OAuth 시작 (리다이렉트) |
| `/auth/oauth/google/callback` | GET | Google OAuth 콜백 (서버 전용) |
| `/auth/oauth/test-token` | POST | 테스트 토큰 발급 (개발용) |
| `/auth/oauth/refresh` | POST | ⭐ Refresh Token으로 Access Token 재발급 |
| `/auth/verify` | POST | JWT 토큰 검증 |
| `/auth/me` | GET | 내 정보 조회 (JWT 필요) |

### API 서버 (localhost:8080)

| 엔드포인트 | 메서드 | 설명 |
|-----------|-------|------|
| `/uploads` | POST | Presigned URL 발급 (업로드용) |
| `/images` | GET | 내 이미지 목록 조회 (JWT 필요) |
| `/images/:key` | GET | 조회용 Presigned URL 발급 |
| `/images/public` | GET | 모든 이미지 목록 (공개) |

---

## 🐛 트러블슈팅

### 1. `useRouter` 에러

```
Error: useRouter must be used in a client component
```

**해결:** 파일 상단에 `'use client'` 추가
```typescript
'use client'

import { useRouter } from 'next/navigation'
```

### 2. QueryClient 에러

```
Only plain objects can be passed to Client Components
```

**해결:** `providers.tsx`에서 `useState`로 QueryClient 생성
```typescript
'use client'

const [queryClient] = useState(() => new QueryClient())
```

### 3. Next.js Image 400 Error (Presigned URL)

```
400 Bad Request when using next/image with Presigned URL
```

**해결:** 일반 `<img>` 태그 사용 (Presigned URL의 서명이 깨지지 않도록)
```typescript
<img src={image.url} alt={image.filename} />
```

### 4. CORS 에러

```
Access to XMLHttpRequest has been blocked by CORS policy
```

**해결:** Auth 서버에서 `http://localhost:3000` 허용 확인
```python
# backend/apps/auth/src/server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. 환경변수가 undefined

**확인 사항:**
- 환경변수에 `NEXT_PUBLIC_` 접두사가 있는지
- `.env` 파일이 루트 디렉토리에 있는지
- 서버 재시작했는지

---

## 📦 의존성

### 주요 라이브러리

```json
{
  "dependencies": {
    "next": "15.1.6",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@tanstack/react-query": "^5.75.7",
    "zustand": "^5.0.4",
    "axios": "^1.7.9"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/react": "^19",
    "eslint": "^9",
    "prettier": "^3.4.2"
  }
}
```

---

## 🚀 Vite → Next.js 마이그레이션 주요 변경사항

| 항목 | Vite + React | Next.js |
|------|-------------|---------|
| **라우팅** | React Router (`react-router-dom`) | App Router (`app/` 디렉토리) |
| **네비게이션** | `useNavigate()` | `useRouter()` from `next/navigation` |
| **환경변수** | `import.meta.env.VITE_*` | `process.env.NEXT_PUBLIC_*` |
| **컴포넌트** | 모두 Client | Server Component (기본), `'use client'` 필요 시 |
| **이미지** | `<img>` | `<Image>` (최적화), Presigned URL은 `<img>` 사용 |
| **개발 모드** | `import.meta.env.DEV` | `process.env.NODE_ENV === 'development'` |

---

## 📚 참고 링크

- **Backend README**: [../backend/README.md](../backend/README.md)
- **Next.js 공식 문서**: https://nextjs.org/docs
- **App Router 가이드**: https://nextjs.org/docs/app

---

## 📝 To-Do

- [x] Next.js 전환 (SEO) ✅
- [x] OAuth 로그인 구현 ✅
- [x] Refresh Token 자동 갱신 ✅
- [x] 이미지 조회 페이지(홈 화면) ✅
- [ ] 이미지 업로드 UI 구현
- [ ] 프로필 페이지 추가
- [x] 로그아웃 버튼 추가
- [ ] 로딩 스피너 컴포넌트
- [ ] 테스트 코드 추가 (Playwright)
- [ ] Vercel? 배포

---

## ⚡ 성능 최적화

### Server Components 활용
- 가능한 모든 컴포넌트를 Server Component로 작성
- Client Component는 필요 시에만 (`'use client'`)

### Image Optimization
- 정적 이미지: `next/image` 사용
- Presigned URL: 일반 `<img>` 사용 (서명 유지)

### Caching
- React Query: 5분 캐싱 (`staleTime: 60 * 1000`)
- Zustand: localStorage persist (로그인 상태 유지)

---

**Made with using Next.js 15**

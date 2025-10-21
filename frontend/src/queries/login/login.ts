import axios from 'axios'

const AUTH_API_BASE =
    import.meta.env.VITE_AUTH_API_BASE || 'http://localhost:8001'

/**
 * Google OAuth 로그인 시작
 * 브라우저를 Auth 서버로 리다이렉트
 */
export const initiateGoogleLogin = () => {
    window.location.href = `${AUTH_API_BASE}/auth/oauth/google`
}

/**
 * URL에서 JWT 토큰 추출
 * OAuth 콜백 페이지에서 사용
 */
export const extractTokenFromUrl = (): string | null => {
    const params = new URLSearchParams(window.location.search)
    return params.get('token')
}

/**
 * JWT 토큰 검증
 */
export const verifyToken = async (token: string) => {
    const response = await axios.post(`${AUTH_API_BASE}/auth/verify`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    })

    if (response.status !== 200) {
        throw new Error('Token verification failed')
    }

    return response.data
}

/**
 * 내 정보 조회
 */
export const getMe = async (token: string) => {
    const response = await axios.get(`${AUTH_API_BASE}/auth/me`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    })

    if (response.status !== 200) {
        throw new Error('Failed to fetch user info')
    }

    return response.data
}

/**
 * 테스트 토큰 발급 (개발용)
 */
export const getTestToken = async (email: string = 'test@example.com') => {
    const response = await axios.post(
        `${AUTH_API_BASE}/auth/oauth/test-token`,
        {
            email,
        },
    )

    if (response.status !== 200) {
        throw new Error('Failed to get test token')
    }

    return response.data
}

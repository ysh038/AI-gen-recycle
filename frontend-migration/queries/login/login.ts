import axios from 'axios'

import { authAxios } from './axios-config'

const AUTH_API_BASE =
    process.env.AUTH_API_BASE || 'http://localhost:8001'

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

// ✅ Refresh Token으로 Access Token 재발급
export const refreshAccessToken = async (
    refreshToken: string,
): Promise<string> => {
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
// ✅ verifyToken도 수정
export const verifyToken = async (token: string) => {
    const response = await authAxios.post('/auth/verify')
    return response.data
}

/**
 * 내 정보 조회
 */
// ✅ getMe 함수 수정 - 401 에러 시 자동 갱신 (refresh token 사용)
export const getMe = async (token: string) => {
    const response = await authAxios.get('/auth/me')
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

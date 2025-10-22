import axios from 'axios'

import { useAuthStore } from '../../stores/shared/user'

const AUTH_API_BASE =
    import.meta.env.VITE_AUTH_API_BASE || 'http://localhost:8001'

// ✅ Axios 인스턴스 생성
export const authAxios = axios.create({
    baseURL: AUTH_API_BASE,
})

// ✅ Request Interceptor: 자동으로 Access Token 추가
authAxios.interceptors.request.use((config) => {
    const token = useAuthStore.getState().token
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// ✅ Response Interceptor: 401 에러 시 자동 갱신
authAxios.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        // 401 에러 + 재시도 아직 안함
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            try {
                const { refreshToken, setToken, logout } =
                    useAuthStore.getState()

                if (!refreshToken) {
                    throw new Error('No refresh token')
                }

                // ✅ Refresh Token으로 새로운 Access Token 발급
                const response = await axios.post(
                    `${AUTH_API_BASE}/auth/oauth/refresh`,
                    {
                        refresh_token: refreshToken,
                    },
                )

                const newAccessToken = response.data.access_token

                // ✅ 새 토큰 저장
                setToken(newAccessToken)

                // ✅ 원래 요청 재시도
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
                return authAxios(originalRequest)
            } catch (refreshError) {
                // Refresh Token도 만료 → 로그아웃
                console.error('Token refresh failed:', refreshError)
                useAuthStore.getState().logout()
                window.location.href = '/login'
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    },
)

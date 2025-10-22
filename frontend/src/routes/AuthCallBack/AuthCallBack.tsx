import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

import { extractTokensFromUrl } from '../../queries/login'
import { useGetMe } from '../../queries/login'
import { useAuthStore } from '../../stores/shared/user'

function AuthCallback() {
    const navigate = useNavigate()
    const { setToken, setRefreshToken, setUser } = useAuthStore() // ✅ setRefreshToken 추가

    useEffect(() => {
        const { token, refreshToken } = extractTokensFromUrl() // ✅ 수정
        if (token && refreshToken) {
            setToken(token)
            setRefreshToken(refreshToken)
        } else {
            console.error('No tokens found in URL')
            navigate('/login')
        }
    }, [setToken, setRefreshToken, navigate])

    const token = useAuthStore((state) => state.token)

    // 토큰으로 사용자 정보 조회
    const { data: userData, isLoading, error } = useGetMe(token, !!token)

    useEffect(() => {
        if (userData) {
            setUser(userData)
            console.log('User info loaded:', userData)
            navigate('/') // 홈으로 이동
        }
    }, [userData, setUser, navigate])

    useEffect(() => {
        if (error) {
            console.error('Failed to fetch user info:', error)
            navigate('/login')
        }
    }, [error, navigate])

    return (
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
            {isLoading ? (
                <>
                    <h2>로그인 중...</h2>
                    <p>잠시만 기다려주세요.</p>
                </>
            ) : (
                <h2>리다이렉트 중...</h2>
            )}
        </div>
    )
}

export default AuthCallback

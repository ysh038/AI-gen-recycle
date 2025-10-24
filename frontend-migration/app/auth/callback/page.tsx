'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

import { extractTokensFromUrl } from '@/queries/login'
import { useGetMe } from '@/queries/login'
import { useAuthStore } from '@/stores/shared/user'

function AuthCallback() {
    const router = useRouter()
    const { setToken, setRefreshToken, setUser } = useAuthStore()

    useEffect(() => {
        const { token, refreshToken } = extractTokensFromUrl()
        if (token && refreshToken) {
            setToken(token)
            setRefreshToken(refreshToken)
        } else {
            console.error('No tokens found in URL')
            router.push('/login')
        }
    }, [setToken, setRefreshToken, router])

    const token = useAuthStore((state) => state.token)

    // 토큰으로 사용자 정보 조회
    const { data: userData, isLoading, error } = useGetMe(token, !!token)

    useEffect(() => {
        if (userData) {
            setUser(userData)
            console.log('User info loaded:', userData)
            router.push('/') // 홈으로 이동
        }
    }, [userData, setUser, router])

    useEffect(() => {
        if (error) {
            console.error('Failed to fetch user info:', error)
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
                <h2>리다이렉트 중...</h2>
            )}
        </div>
    )
}

export default AuthCallback

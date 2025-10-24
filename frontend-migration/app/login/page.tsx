'use client'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/shared/user'
import { useGetTestToken, initiateGoogleLogin } from '@/queries/login'

function Login() {
    const testTokenMutation = useGetTestToken()
    const router = useRouter()

    const handleGoogleLogin = () => {
        initiateGoogleLogin()
    }

    const handleTestLogin = () => {
        testTokenMutation.mutate('test@example.com', {
            onSuccess: () => {
                console.log('✅ Test login success, redirecting...')
                router.push('/')
            },
        })
    }
    return (
        <main>
            <h1>로그인</h1>

            <div>
                <button
                    onClick={handleGoogleLogin}
                >
                    🔐 Google로 로그인
                </button>

                {/* 개발 환경에서만 표시 */}
                {process.env.NODE_ENV === 'development' && (
                    <button
                        onClick={handleTestLogin}
                        disabled={testTokenMutation.isPending}
                    >
                        {testTokenMutation.isPending
                            ? '로딩중...'
                            : '🧪 테스트 로그인'}
                    </button>
                )}
            </div>
        </main>
    )
}

export default Login

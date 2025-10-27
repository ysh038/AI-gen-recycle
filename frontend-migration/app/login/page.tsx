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
        <main className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-2xl font-bold">로그인</h1>
            <div className="flex flex-col items-center justify-center gap-4">
                <button
                    onClick={handleGoogleLogin}
                    className="bg-blue-500 text-white p-2 rounded-md"
                >
                    🔐 Google로 로그인
                </button>

                {/* 개발 환경에서만 표시 */}
                {process.env.NODE_ENV === 'development' && (
                    <button
                        onClick={handleTestLogin}
                        disabled={testTokenMutation.isPending}
                        className="bg-blue-500 text-white p-2 rounded-md"
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

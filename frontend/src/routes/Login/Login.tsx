// src/routes/Login/Login.tsx
import { useNavigate } from 'react-router-dom'

import styles from './Login.module.css'
import { useGetTestToken, initiateGoogleLogin } from '../../queries/login'

function Login() {
    const testTokenMutation = useGetTestToken()
    const navigate = useNavigate()

    const handleGoogleLogin = () => {
        initiateGoogleLogin()
    }

    const handleTestLogin = () => {
        testTokenMutation.mutate('test@example.com', {
            onSuccess: () => {
                console.log('✅ Test login success, redirecting...')
                navigate('/') // ✅ 홈으로 이동
            },
        })
    }
    return (
        <main className={styles.main}>
            <h1>로그인</h1>

            <div className={styles.buttons}>
                <button
                    onClick={handleGoogleLogin}
                    className={styles.googleBtn}
                >
                    🔐 Google로 로그인
                </button>

                {/* 개발 환경에서만 표시 */}
                {import.meta.env.DEV && (
                    <button
                        onClick={handleTestLogin}
                        className={styles.testBtn}
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

// src/routes/Login/Login.tsx
import styles from './Login.module.css'
import { useGetTestToken, initiateGoogleLogin } from '../../queries/login'

function Login() {
    const testTokenMutation = useGetTestToken()

    const handleGoogleLogin = () => {
        initiateGoogleLogin()
    }

    const handleTestLogin = () => {
        testTokenMutation.mutate('test@example.com')
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

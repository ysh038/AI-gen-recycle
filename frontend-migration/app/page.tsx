'use client'
import { useAuthStore } from '../stores/shared/user'
import { useRouter } from 'next/navigation'

function Home() {
    const user = useAuthStore((state) => state.user)
    const { logout } = useAuthStore()
    const router = useRouter()

    const handleLogout = () => {
        logout()
        router.push('/login')
    }

    return (
        <main>
            <h1>테스트 로그인 성공</h1>
            <p>사용자 정보: {user?.user_id}</p>
            <p>이메일: {user?.email}</p>
            <div>
                <button onClick={handleLogout}>로그아웃</button>
            </div>
        </main>
    )
}

export default Home

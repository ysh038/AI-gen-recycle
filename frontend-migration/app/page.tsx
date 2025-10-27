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
        <main className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-2xl font-bold">테스트 로그인 성공</h1>
            <p className="text-lg">사용자 정보: {user?.user_id}</p>
            <p className="text-lg">이메일: {user?.email}</p>
            <div>
                <button onClick={handleLogout} className="bg-blue-500 text-white p-2 rounded-md">로그아웃</button>
            </div>
        </main>
    )
}

export default Home

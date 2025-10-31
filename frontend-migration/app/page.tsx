'use client'
import { NavBar } from '@/components/shared'
import { useAuthStore } from '../stores/shared/user'
import { useRouter } from 'next/navigation'
import Images from '@/components/home/Images'

function Home() {
    const user = useAuthStore((state) => state.user)
    const { logout } = useAuthStore()
    const router = useRouter()

    const handleLogout = () => {
        logout()
        router.push('/login')
    }

    return (
        <main className="">
            <NavBar />
            <div className="flex flex-col items-center justify-center">
                <h1 className="text-2xl font-bold">테스트 로그인 성공</h1>
                <p className="text-lg">사용자 정보: {user?.name}</p>
                <p className="text-lg">이메일: {user?.email}</p>
                <div>
                    <button
                        onClick={handleLogout}
                        className="bg-blue-500 text-white p-2 rounded-md"
                    >
                        로그아웃
                    </button>
                </div>
            </div>
            <Images />
        </main>
    )
}

export default Home

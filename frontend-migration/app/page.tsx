'use client'
import { NavBar } from '@/components/shared'
import { useAuthStore } from '../stores/shared/user'
import { useRouter } from 'next/navigation'
import Images from '@/components/home/Images'
import { useEffect } from 'react'

function Home() {
    const user = useAuthStore((state) => state.user)
    const { logout } = useAuthStore()
    const router = useRouter()

    const handleLogout = () => {
        logout()
        router.push('/login')
    }

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-950 to-slate-900">
            <NavBar />
            
            {/* Hero Section */}
            <div className="flex flex-col items-center justify-center px-6 py-16 space-y-8">
                {/* Glass Card */}
                <div className="backdrop-blur-lg bg-white/5 border border-emerald-500/20 rounded-2xl p-8 shadow-2xl shadow-emerald-500/10 max-w-md w-full">
                    {/* Success Badge */}
                    <div className="flex items-center justify-center mb-6">
                        <div className="bg-emerald-500/20 px-4 py-2 rounded-full border border-emerald-400/30">
                            {user?.user_id ? <span className="text-emerald-300 text-sm font-medium">
                                ✓ 로그인 완료
                            </span> : <span className="text-red-300 text-sm font-medium">
                                미 로그인
                            </span>}
                        </div>
                    </div>
                    
                    {/* User Info */}
                    <div className="text-center space-y-4">
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-300 to-teal-300 bg-clip-text text-transparent">
                            Welcome, Echo
                        </h1>
                        
                        <div className="space-y-2 text-slate-300">
                            <p className="flex items-center justify-center gap-2">
                                <span className="text-emerald-400">👤</span>
                                <span className="text-lg">{user?.name || '사용자'}</span>
                            </p>
                            <p className="flex items-center justify-center gap-2">
                                <span className="text-emerald-400">✉️</span>
                                <span className="text-sm text-slate-400">{user?.email}</span>
                            </p>
                        </div>
                    </div>
                    
                    {/* Divider */}
                    <div className="my-6 h-px bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent" />
                    
                    {/* Logout Button */}
                    <button
                        onClick={handleLogout}
                        className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium py-3 px-6 rounded-xl transition-all duration-300 shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:scale-[1.02] active:scale-[0.98]"
                    >
                        로그아웃
                    </button>
                </div>
                
                {/* Environment Tag */}
                <div className="text-center">
                    <p className="text-emerald-400/60 text-sm font-light tracking-wider">
                        SUSTAINABLE • RECYCLABLE • ECO-FRIENDLY
                    </p>
                </div>
            </div>
            
            {/* Images Section with dark theme */}
            <div className="px-4 pb-16">
                <Images />
            </div>
        </main>
    )
}

export default Home

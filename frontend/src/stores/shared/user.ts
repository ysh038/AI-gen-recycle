// src/stores/shared/index.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface IUser {
    user_id: number
    email: string
    name?: string
}

interface IAuthState {
    token: string | null
    refreshToken: string | null // ✅ 추가
    user: IUser | null
    setToken: (token: string | null) => void
    setRefreshToken: (refreshToken: string | null) => void // ✅ 추가
    setUser: (user: IUser | null) => void
    logout: () => void
    isAuthenticated: () => boolean
}

export const useAuthStore = create<IAuthState>()(
    persist(
        (set, get) => ({
            token: null,
            refreshToken: null, // ✅ 추가
            user: null,

            setToken: (token) => set({ token }),

            setRefreshToken: (refreshToken) => set({ refreshToken }), // ✅ 추가

            setUser: (user) => set({ user }),

            logout: () => set({ token: null, refreshToken: null, user: null }), // ✅ 수정

            isAuthenticated: () => {
                const { token } = get()
                return !!token
            },
        }),
        {
            name: 'auth-storage',
        },
    ),
)

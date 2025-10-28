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
    refreshToken: string | null
    user: IUser | null
    setToken: (token: string | null) => void
    setRefreshToken: (refreshToken: string | null) => void
    setUser: (user: IUser | null) => void
    logout: () => void
    isAuthenticated: () => boolean
}

export const useAuthStore = create<IAuthState>()(
    persist(
        (set, get) => ({
            token: null,
            refreshToken: null,
            user: null,

            setToken: (token) => set({ token }),

            setRefreshToken: (refreshToken) => set({ refreshToken }),

            setUser: (user) => set({ user }),

            logout: () => set({ token: null, refreshToken: null, user: null }),

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

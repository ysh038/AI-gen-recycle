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
    user: IUser | null
    setToken: (token: string | null) => void
    setUser: (user: IUser | null) => void
    logout: () => void
    isAuthenticated: () => boolean
}

export const useAuthStore = create<IAuthState>()(
    persist(
        (set, get) => ({
            token: null,
            user: null,

            setToken: (token) => set({ token }),

            setUser: (user) => set({ user }),

            logout: () => set({ token: null, user: null }),

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

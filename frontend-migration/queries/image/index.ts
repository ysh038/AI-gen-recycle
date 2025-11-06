import { useQuery } from '@tanstack/react-query'
import { getMyImages, getPublicImages } from './image'
import { useAuthStore } from '@/stores/shared/user'

/**
 * 공개 이미지 목록 조회 (인증 불필요) ⭐
 */
export const usePublicImages = (skip = 0, limit = 50) => {
    return useQuery({
        queryKey: ['images', 'public', skip, limit],
        queryFn: () => getPublicImages(skip, limit),
        staleTime: 1000 * 60,
    })
}

/**
 * 내 이미지 목록 조회 훅
 */
export const useMyImages = (skip = 0, limit = 50) => {
    const token = useAuthStore((state) => state.token)

    return useQuery({
        queryKey: ['images', 'my', skip, limit],
        queryFn: () => {
            if (!token) throw new Error('No token')
            return getMyImages(token, skip, limit)
        },
        enabled: !!token,
        staleTime: 1000 * 60, // 1분
    })
}

export * from './image'

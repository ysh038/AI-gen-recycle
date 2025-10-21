import { useMutation, useQuery } from '@tanstack/react-query';
import { verifyToken, getMe, getTestToken } from './login';
import { useAuthStore } from '../../stores/shared/user';

/**
 * 토큰 검증 훅
 */
export const useVerifyToken = () => {
  return useMutation({
    mutationFn: (token: string) => verifyToken(token),
    onSuccess: (data) => {
      console.log('Token verified:', data);
    },
    onError: (error) => {
      console.error('Token verification failed:', error);
    },
  });
};

/**
 * 사용자 정보 조회 훅
 */
export const useGetMe = (token: string | null, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['user', 'me', token],
    queryFn: () => {
      if (!token) throw new Error('No token provided');
      return getMe(token);
    },
    enabled: enabled && !!token,
    staleTime: 1000 * 60 * 5, // 5분
  });
};

/**
 * 테스트 토큰 발급 훅 (개발용)
 */
export const useGetTestToken = () => {
  const { setToken, setUser } = useAuthStore();

  return useMutation({
    mutationFn: (email?: string) => getTestToken(email),
    onSuccess: (data) => {
            setToken(data.access_token)
            setUser(data.user)
            console.log('Test token acquired:', data)
        },
        onError: (error) => {
            console.error('Failed to get test token:', error)
        },
    })
};

export * from './login'
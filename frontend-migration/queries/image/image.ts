import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8080'

export interface ImageItem {
  id: number
  key: string
  filename: string
  size: number
  url: string  // ✅ Presigned URL
  created_at: string
}

export interface ImageListResponse {
  images: ImageItem[]
  count: number
}

/**
 * 내 이미지 목록 조회
 */
export async function getMyImages(
  token: string,
  skip: number = 0,
  limit: number = 50
): Promise<ImageListResponse> {
  const response = await axios.get(`${API_BASE}/images`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    params: {
      skip,
      limit,
    },
  })
  
  return response.data
}
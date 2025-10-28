'use client'

import { useMyImages } from '@/queries/image'
import Image from 'next/image'

export default function Images() {
    function formatFileSize(bytes: number): string {
        if (bytes < 1024) return `${bytes} B`
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    }

    function formatDate(isoString: string): string {
        const date = new Date(isoString)
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        })
    }

    const { data, isLoading, error } = useMyImages()

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-xl">이미지 로딩 중...</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-red-500">
                    에러 발생:{' '}
                    {error instanceof Error ? error.message : '알 수 없는 오류'}
                </div>
            </div>
        )
    }

    if (!data || data.images.length === 0) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-gray-500">업로드한 이미지가 없습니다.</div>
            </div>
        )
    }

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6">내 이미지</h1>

            <div className="text-sm text-gray-500 mb-4">
                총 {data.count}개의 이미지
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {data.images.map((image) => (
                    <div
                        key={image.id}
                        className="border rounded-lg overflow-hidden shadow hover:shadow-lg transition"
                    >
                        {/* ✅ 핵심: presigned URL을 img src에 사용 */}
                        <img
                            src={image.url}
                            width={300}
                            height={300}
                            alt={image.filename}
                            className="w-full h-48 object-cover"
                        />

                        <div className="p-3">
                            <p
                                className="text-sm font-medium truncate"
                                title={image.filename}
                            >
                                {image.filename}
                            </p>
                            <div className="text-xs text-gray-500 mt-1">
                                <p>{formatFileSize(image.size)}</p>
                                <p>{formatDate(image.created_at)}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

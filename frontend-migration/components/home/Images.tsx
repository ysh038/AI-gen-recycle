'use client'

import { useMyImages } from '@/queries/image'

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
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="flex flex-col items-center gap-4">
                    {/* Loading Spinner */}
                    <div className="w-16 h-16 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
                    <p className="text-emerald-300 text-lg font-medium">이미지 로딩 중...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="backdrop-blur-lg bg-red-500/10 border border-red-500/30 rounded-xl p-6 max-w-md">
                    <div className="flex items-center gap-3 mb-2">
                        <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <h3 className="text-red-400 font-semibold">에러 발생</h3>
                    </div>
                    <p className="text-red-300/80 text-sm">
                        {error instanceof Error ? error.message : '알 수 없는 오류'}
                    </p>
                </div>
            </div>
        )
    }

    if (!data || data.images.length === 0) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="backdrop-blur-lg bg-white/5 border border-emerald-500/20 rounded-2xl p-8 text-center max-w-md">
                    <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-emerald-500/10 flex items-center justify-center">
                        <svg className="w-10 h-10 text-emerald-400/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <h3 className="text-emerald-300 text-xl font-semibold mb-2">이미지가 없습니다</h3>
                    <p className="text-slate-400 text-sm">첫 번째 이미지를 업로드해보세요</p>
                </div>
            </div>
        )
    }

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header Section */}
            <div className="mb-8 space-y-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-300 to-teal-300 bg-clip-text text-transparent">
                        내 이미지
                    </h1>
                </div>
                
                <div className="flex items-center gap-2 text-emerald-400/80">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span className="text-sm font-medium">
                        총 {data.count}개의 이미지
                    </span>
                </div>
            </div>

            {/* Image Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {data.images.map((image) => (
                    <div
                        key={image.id}
                        className="group backdrop-blur-lg bg-white/5 border border-emerald-500/20 rounded-xl overflow-hidden shadow-lg shadow-emerald-500/5 hover:shadow-2xl hover:shadow-emerald-500/20 hover:border-emerald-500/40 transition-all duration-300 hover:scale-[1.02]"
                    >
                        {/* Image Container */}
                        <div className="relative h-48 bg-slate-800/50 overflow-hidden">
                            <img
                                src={image.url}
                                alt={image.filename}
                                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                            />
                            
                            {/* Overlay on Hover */}
                            <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                <div className="absolute bottom-2 left-2 right-2">
                                    <div className="flex items-center gap-2 text-xs text-emerald-300">
                                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                        </svg>
                                        <span>클릭하여 확대</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Info Section */}
                        <div className="p-4 space-y-3">
                            {/* Filename */}
                            <p
                                className="text-sm font-semibold text-emerald-200 truncate"
                                title={image.filename}
                            >
                                {image.filename}
                            </p>
                            
                            {/* Metadata */}
                            <div className="space-y-2 text-xs text-slate-400">
                                {/* File Size */}
                                <div className="flex items-center gap-2">
                                    <svg className="w-3.5 h-3.5 text-emerald-500/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                    </svg>
                                    <span>{formatFileSize(image.size)}</span>
                                </div>
                                
                                {/* Upload Date */}
                                <div className="flex items-center gap-2">
                                    <svg className="w-3.5 h-3.5 text-emerald-500/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <span>{formatDate(image.created_at)}</span>
                                </div>
                                
                                {/* Uploader */}
                                <div className="flex items-center gap-2">
                                    <svg className="w-3.5 h-3.5 text-emerald-500/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                    </svg>
                                    <span className="text-emerald-400/80">{image.user.name}</span>
                                </div>
                            </div>
                            
                            {/* Eco Badge */}
                            <div className="pt-2 border-t border-emerald-500/10">
                                <span className="inline-flex items-center gap-1 px-2 py-1 text-[10px] font-medium text-emerald-400/70 bg-emerald-500/10 rounded-full">
                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    Eco Stored
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

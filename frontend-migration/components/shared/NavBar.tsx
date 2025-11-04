import Link from 'next/link'

function NavBar() {
    return (
        <nav className="sticky top-0 z-50 backdrop-blur-md bg-slate-900/80 border-b border-emerald-500/20 shadow-lg shadow-emerald-500/5">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo Section */}
                    <div className="flex items-center gap-3">
                        {/* Eco Icon */}
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/30">
                            <svg 
                                className="w-6 h-6 text-white" 
                                fill="none" 
                                stroke="currentColor" 
                                viewBox="0 0 24 24"
                            >
                                <path 
                                    strokeLinecap="round" 
                                    strokeLinejoin="round" 
                                    strokeWidth={2} 
                                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
                                />
                            </svg>
                        </div>
                        
                        {/* Brand Name */}
                        <div>
                            <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-300 to-teal-300 bg-clip-text text-transparent">
                                Echo Recycle
                            </h1>
                            <p className="text-xs text-emerald-400/60 -mt-1">
                                Sustainable Future
                            </p>
                        </div>
                    </div>
                    
                    {/* Actions Section */}
                    <div className="flex items-center gap-4">
                        <Link href="/gallery">
                            <button className="hidden sm:flex items-center gap-2 px-4 py-2 text-emerald-300 hover:text-emerald-200 transition-colors duration-300">
                                <svg 
                                    className="w-5 h-5" 
                                    fill="none" 
                                    stroke="currentColor" 
                                    viewBox="0 0 24 24"
                                >
                                    <path 
                                        strokeLinecap="round" 
                                        strokeLinejoin="round" 
                                        strokeWidth={2} 
                                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" 
                                    />
                                </svg>
                                <span className="text-sm font-medium">Gallery</span>
                            </button>
                        </Link>
                        
                        <Link href="/login">
                            <button className="group relative px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium rounded-lg transition-all duration-300 shadow-md shadow-emerald-500/25 hover:shadow-lg hover:shadow-emerald-500/40 hover:scale-[1.02] active:scale-[0.98]">
                                <span className="flex items-center gap-2">
                                    <svg 
                                        className="w-4 h-4" 
                                        fill="none" 
                                        stroke="currentColor" 
                                        viewBox="0 0 24 24"
                                    >
                                        <path 
                                            strokeLinecap="round" 
                                            strokeLinejoin="round" 
                                            strokeWidth={2} 
                                            d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" 
                                        />
                                    </svg>
                                    Login
                                </span>
                            </button>
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    )
}

export default NavBar
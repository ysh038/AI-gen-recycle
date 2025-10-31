import Link from 'next/link'

function NavBar() {
    return (
        <nav className="flex justify-between items-center p-4">
            <h1 className="text-2xl font-bold">AI-gen-recycle</h1>
            <div className="flex items-center gap-4">
                <Link href="/login">
                    <button className="bg-blue-500 text-white p-2 rounded-md">
                        Login
                    </button>
                </Link>
            </div>
        </nav>
    )
}

export default NavBar
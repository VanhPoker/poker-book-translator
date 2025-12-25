import Link from 'next/link'

export default function Header() {
    return (
        <header className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50">
            <div className="max-w-7xl mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-3 group">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 
                            flex items-center justify-center text-xl
                            group-hover:scale-110 transition-transform duration-300">
                            🃏
                        </div>
                        <span className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 
                             bg-clip-text text-transparent">
                            Poker Book Translator
                        </span>
                    </Link>

                    <nav className="flex items-center gap-6">
                        <Link
                            href="/"
                            className="text-slate-300 hover:text-white transition-colors"
                        >
                            Thư viện
                        </Link>
                    </nav>
                </div>
            </div>
        </header>
    )
}

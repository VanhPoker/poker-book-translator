'use client'

import Link from 'next/link'
import { useTheme } from '@/contexts/ThemeContext'

export default function Header() {
    const { theme, toggleTheme } = useTheme()

    return (
        <header className={`fixed top-0 left-0 right-0 z-50 border-b shadow-lg transition-all duration-300
                          ${theme === 'dark'
                ? 'bg-gradient-to-r from-amber-950 via-stone-900 to-amber-950 border-amber-800/30 shadow-amber-950/50'
                : 'bg-gradient-to-r from-amber-100 via-amber-50 to-amber-100 border-amber-300/50 shadow-amber-200/50'}`}>
            <div className="max-w-7xl mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-3 group">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center border shadow-lg overflow-hidden
                                      transition-all duration-300
                                      ${theme === 'dark'
                                ? 'bg-white border-amber-500/30'
                                : 'bg-white border-amber-400/50'}`}>
                            <img src="/logo.png" alt="Logo" className="w-8 h-8 object-contain" />
                        </div>
                        <div>
                            <span className={`font-serif text-xl font-bold transition-colors
                                           ${theme === 'dark' ? 'text-amber-100 group-hover:text-amber-50' : 'text-amber-900 group-hover:text-amber-700'}`}>
                                Thư Viện Poker
                            </span>
                            <div className={`text-xs ${theme === 'dark' ? 'text-amber-500/60' : 'text-amber-700/70'}`}>
                                Thư viện sách poker tiếng việt
                            </div>
                        </div>
                    </Link>

                    {/* Navigation */}
                    <nav className="flex items-center gap-4">
                        {/* <Link
                            href="/"
                            className={`transition-colors font-serif flex items-center gap-2
                                      ${theme === 'dark' ? 'text-amber-300/80 hover:text-amber-100' : 'text-amber-700 hover:text-amber-900'}`}
                        >
                            <span>📚</span>
                            Kệ sách
                        </Link> */}

                        {/* Theme Toggle Button */}
                        <button
                            onClick={toggleTheme}
                            className={`p-2 rounded-lg transition-all duration-300 border
                                      ${theme === 'dark'
                                    ? 'bg-amber-900/50 border-amber-700/50 hover:bg-amber-800/50 text-amber-200'
                                    : 'bg-amber-200/50 border-amber-400/50 hover:bg-amber-300/50 text-amber-800'}`}
                            title={theme === 'dark' ? 'Chuyển sang Light Mode' : 'Chuyển sang Dark Mode'}
                        >
                            {theme === 'dark' ? '☀️' : '🌙'}
                        </button>
                    </nav>
                </div>
            </div>
        </header>
    )
}

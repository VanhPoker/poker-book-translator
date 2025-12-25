'use client'

import { useTheme } from '@/contexts/ThemeContext'
import { useState, useEffect } from 'react'

interface SearchBarProps {
    onSearch: (query: string) => void
    placeholder?: string
}

export default function SearchBar({ onSearch, placeholder = "Tìm kiếm sách..." }: SearchBarProps) {
    const { theme } = useTheme()
    const [query, setQuery] = useState('')
    const isDark = theme === 'dark'

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            onSearch(query)
        }, 300)

        return () => clearTimeout(timer)
    }, [query, onSearch])

    const handleClear = () => {
        setQuery('')
        onSearch('')
    }

    return (
        <div className="relative w-full max-w-md mx-auto">
            <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-lg">
                    🔍
                </span>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={placeholder}
                    className={`w-full pl-12 pr-10 py-3 rounded-full border-2 
                               transition-all duration-300 focus:outline-none
                               ${isDark
                            ? 'bg-stone-900 border-amber-800/50 text-amber-100 placeholder-amber-400/50 focus:border-amber-600'
                            : 'bg-white border-amber-300 text-amber-900 placeholder-amber-500/60 focus:border-amber-500'}`}
                />
                {query && (
                    <button
                        onClick={handleClear}
                        className={`absolute right-4 top-1/2 -translate-y-1/2 
                                   transition-colors hover:scale-110
                                   ${isDark ? 'text-amber-400 hover:text-amber-200' : 'text-amber-600 hover:text-amber-800'}`}
                    >
                        ✕
                    </button>
                )}
            </div>
        </div>
    )
}

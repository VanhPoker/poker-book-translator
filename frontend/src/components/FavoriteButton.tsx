'use client'

import { useTheme } from '@/contexts/ThemeContext'
import { useAuth } from '@/contexts/AuthContext'
import { useState, useEffect } from 'react'
import { isFavorite, addToFavorites, removeFromFavorites } from '@/lib/supabase'

interface FavoriteButtonProps {
    bookId: string
    onToggle?: (isFav: boolean) => void
}

export default function FavoriteButton({ bookId, onToggle }: FavoriteButtonProps) {
    const { theme } = useTheme()
    const { user } = useAuth()
    const [favorite, setFavorite] = useState(false)
    const [loading, setLoading] = useState(false)
    const isDark = theme === 'dark'

    // Check if book is in favorites on mount
    useEffect(() => {
        async function checkFavorite() {
            if (user) {
                const isFav = await isFavorite(bookId, user.id)
                setFavorite(isFav)
            }
        }
        checkFavorite()
    }, [bookId, user])

    const handleToggle = async () => {
        if (!user) {
            alert('Vui lòng đăng nhập để lưu sách yêu thích!')
            return
        }

        setLoading(true)

        if (favorite) {
            const success = await removeFromFavorites(bookId, user.id)
            if (success) {
                setFavorite(false)
                onToggle?.(false)
            }
        } else {
            const success = await addToFavorites(bookId, user.id)
            if (success) {
                setFavorite(true)
                onToggle?.(true)
            }
        }

        setLoading(false)
    }

    return (
        <button
            onClick={handleToggle}
            disabled={loading}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-300
                       flex items-center gap-2 hover:scale-105
                       ${favorite
                    ? 'bg-pink-600 text-white hover:bg-pink-500'
                    : isDark
                        ? 'bg-stone-700 text-amber-100 hover:bg-stone-600'
                        : 'bg-amber-100 text-amber-800 hover:bg-amber-200'}`}
        >
            <span className={`text-lg ${favorite ? 'animate-pulse' : ''}`}>
                {favorite ? '❤️' : '🤍'}
            </span>
            <span>
                {loading ? '...' : favorite ? 'Đã lưu' : 'Yêu thích'}
            </span>
        </button>
    )
}

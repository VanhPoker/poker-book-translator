'use client'

import { useTheme } from '@/contexts/ThemeContext'
import { useState } from 'react'

interface RatingStarsProps {
    rating: number
    onRate?: (rating: number) => void
    readonly?: boolean
    size?: 'sm' | 'md' | 'lg'
    showCount?: number
}

export default function RatingStars({
    rating,
    onRate,
    readonly = false,
    size = 'md',
    showCount
}: RatingStarsProps) {
    const { theme } = useTheme()
    const [hoverRating, setHoverRating] = useState(0)
    const isDark = theme === 'dark'

    const sizeClasses = {
        sm: 'text-lg',
        md: 'text-2xl',
        lg: 'text-3xl'
    }

    const stars = [1, 2, 3, 4, 5]

    const handleClick = (star: number) => {
        if (!readonly && onRate) {
            onRate(star)
        }
    }

    return (
        <div className="flex items-center gap-1">
            <div className="flex">
                {stars.map((star) => {
                    const isFilled = star <= (hoverRating || rating)
                    return (
                        <button
                            key={star}
                            type="button"
                            onClick={() => handleClick(star)}
                            onMouseEnter={() => !readonly && setHoverRating(star)}
                            onMouseLeave={() => !readonly && setHoverRating(0)}
                            disabled={readonly}
                            className={`${sizeClasses[size]} transition-all duration-200
                                       ${readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110'}
                                       ${isFilled
                                    ? 'text-amber-500'
                                    : isDark ? 'text-stone-600' : 'text-amber-200'}`}
                        >
                            ★
                        </button>
                    )
                })}
            </div>

            {(showCount !== undefined && showCount > 0) && (
                <span className={`ml-2 text-sm ${isDark ? 'text-amber-400/60' : 'text-amber-600/70'}`}>
                    ({showCount} đánh giá)
                </span>
            )}

            {rating > 0 && !showCount && (
                <span className={`ml-2 text-sm font-medium ${isDark ? 'text-amber-300' : 'text-amber-700'}`}>
                    {rating.toFixed(1)}
                </span>
            )}
        </div>
    )
}

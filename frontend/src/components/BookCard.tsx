'use client'

import Link from 'next/link'
import { useTheme } from '@/contexts/ThemeContext'

// Category display config
const CATEGORY_CONFIG: Record<string, { name: string; icon: string; color: string }> = {
    nlh: { name: 'NLH', icon: '♠️', color: 'bg-blue-600' },
    omaha: { name: 'Omaha', icon: '♥️', color: 'bg-red-600' },
    shortdeck: { name: 'Short Deck', icon: '♦️', color: 'bg-orange-600' },
    ai_research: { name: 'AI/GTO', icon: '🤖', color: 'bg-purple-600' },
    psychology: { name: 'Tâm lí', icon: '🧠', color: 'bg-pink-600' },
    general: { name: 'Tổng hợp', icon: '♣️', color: 'bg-stone-600' },
}

interface BookCardProps {
    id: string
    title: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    coverUrl?: string | null
    createdAt?: string | null
    category?: string | null
}

export default function BookCard({ id, title, status, coverUrl, createdAt, category }: BookCardProps) {
    const { theme } = useTheme()

    const statusConfig = {
        pending: { label: 'Chờ xử lý', color: 'bg-amber-600', icon: '⏳' },
        processing: { label: 'Đang dịch', color: 'bg-blue-600', icon: '🔄' },
        completed: { label: 'Hoàn thành', color: 'bg-emerald-600', icon: '✓' },
        failed: { label: 'Thất bại', color: 'bg-red-600', icon: '✗' }
    }

    const { label, color, icon } = statusConfig[status]
    const catConfig = category && CATEGORY_CONFIG[category] ? CATEGORY_CONFIG[category] : null

    const formattedDate = createdAt
        ? new Date(createdAt).toLocaleDateString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        })
        : ''

    return (
        <Link
            href={`/books/${id}`}
            className="group block"
        >
            {/* Book Card */}
            <div className={`relative rounded-lg overflow-hidden transition-all duration-300 hover:-translate-y-1
                          ${theme === 'dark'
                    ? 'bg-gradient-to-b from-amber-900/20 to-amber-950/40 border border-amber-800/30 hover:border-amber-600/50 hover:shadow-2xl hover:shadow-amber-900/20'
                    : 'bg-gradient-to-b from-amber-100 to-amber-200/80 border border-amber-300/50 hover:border-amber-400 hover:shadow-xl hover:shadow-amber-300/30'}`}>

                {/* Cover Image */}
                <div className={`relative aspect-[3/4] overflow-hidden
                              ${theme === 'dark'
                        ? 'bg-gradient-to-br from-amber-800 to-amber-950'
                        : 'bg-gradient-to-br from-amber-200 to-amber-300'}`}>
                    {coverUrl ? (
                        <img
                            src={coverUrl}
                            alt={title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                    ) : (
                        <div className="w-full h-full flex items-center justify-center">
                            <div className="text-center">
                                <div className="text-6xl mb-2">📚</div>
                                <div className={`text-sm ${theme === 'dark' ? 'text-amber-300/50' : 'text-amber-600/70'}`}>
                                    Không có bìa
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Status Badge */}
                    <div className={`absolute top-3 right-3 ${color} px-2 py-1 rounded text-xs font-medium text-white shadow-lg`}>
                        <span className="mr-1">{icon}</span>
                        {label}
                    </div>

                    {/* Category Badge */}
                    {catConfig && (
                        <div className={`absolute top-3 left-3 ${catConfig.color} px-2 py-1 rounded text-xs font-medium text-white shadow-lg`}>
                            <span className="mr-1">{catConfig.icon}</span>
                            {catConfig.name}
                        </div>
                    )}

                    {/* Gradient Overlay */}
                    <div className={`absolute inset-0 ${theme === 'dark'
                        ? 'bg-gradient-to-t from-amber-950 via-transparent to-transparent opacity-60'
                        : 'bg-gradient-to-t from-amber-200 via-transparent to-transparent opacity-40'}`}></div>
                </div>

                {/* Book Info */}
                <div className={`p-4 ${theme === 'dark'
                    ? 'bg-gradient-to-b from-amber-950/80 to-stone-900'
                    : 'bg-gradient-to-b from-amber-100 to-amber-50'}`}>
                    <h3 className={`font-serif font-semibold text-lg leading-snug line-clamp-2 mb-2 transition-colors
                                  ${theme === 'dark'
                            ? 'text-amber-100 group-hover:text-amber-50'
                            : 'text-amber-900 group-hover:text-amber-700'}`}>
                        {title}
                    </h3>

                    <div className={`flex items-center text-sm ${theme === 'dark' ? 'text-amber-400/60' : 'text-amber-600/80'}`}>
                        <span className="mr-1">📅</span>
                        {formattedDate}
                    </div>
                </div>

                {/* Book spine effect */}
                <div className={`absolute left-0 top-0 bottom-0 w-1 ${theme === 'dark'
                    ? 'bg-gradient-to-b from-amber-600 via-amber-800 to-amber-950'
                    : 'bg-gradient-to-b from-amber-400 via-amber-500 to-amber-600'}`}></div>
            </div>
        </Link>
    )
}

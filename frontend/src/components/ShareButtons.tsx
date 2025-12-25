'use client'

import { useTheme } from '@/contexts/ThemeContext'
import { useState } from 'react'

interface ShareButtonsProps {
    title: string
    url?: string
}

export default function ShareButtons({ title, url }: ShareButtonsProps) {
    const { theme } = useTheme()
    const [copied, setCopied] = useState(false)

    // Use current URL if not provided
    const shareUrl = url || (typeof window !== 'undefined' ? window.location.href : '')
    const encodedUrl = encodeURIComponent(shareUrl)
    const encodedTitle = encodeURIComponent(title)

    const isDark = theme === 'dark'

    const handleCopyLink = async () => {
        try {
            await navigator.clipboard.writeText(shareUrl)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        } catch (err) {
            console.error('Failed to copy:', err)
        }
    }

    const shareLinks = [
        {
            name: 'Facebook',
            icon: '📘',
            url: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedTitle}`,
            color: 'bg-blue-600 hover:bg-blue-500'
        },
        {
            name: 'Zalo',
            icon: '💬',
            url: `https://zalo.me/share/?url=${encodedUrl}&title=${encodedTitle}`,
            color: 'bg-blue-500 hover:bg-blue-400'
        },
        {
            name: 'Telegram',
            icon: '✈️',
            url: `https://t.me/share/url?url=${encodedUrl}&text=${encodedTitle}`,
            color: 'bg-sky-500 hover:bg-sky-400'
        },
        {
            name: 'Twitter',
            icon: '🐦',
            url: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
            color: 'bg-black hover:bg-gray-800'
        }
    ]

    return (
        <div className="flex flex-wrap gap-2 items-center">
            <span className={`text-sm mr-2 ${isDark ? 'text-amber-300/70' : 'text-amber-700'}`}>
                Chia sẻ:
            </span>

            {shareLinks.map((link) => (
                <a
                    key={link.name}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={`Chia sẻ lên ${link.name}`}
                    className={`${link.color} text-white px-3 py-1.5 rounded-full text-sm 
                               transition-all duration-300 hover:scale-105 hover:shadow-lg
                               flex items-center gap-1`}
                >
                    <span>{link.icon}</span>
                    <span className="hidden sm:inline">{link.name}</span>
                </a>
            ))}

            <button
                onClick={handleCopyLink}
                title="Copy link"
                className={`px-3 py-1.5 rounded-full text-sm transition-all duration-300 
                           hover:scale-105 flex items-center gap-1
                           ${copied
                        ? 'bg-green-600 text-white'
                        : isDark
                            ? 'bg-stone-700 hover:bg-stone-600 text-amber-100'
                            : 'bg-amber-200 hover:bg-amber-300 text-amber-900'}`}
            >
                <span>{copied ? '✓' : '🔗'}</span>
                <span className="hidden sm:inline">{copied ? 'Đã copy!' : 'Copy link'}</span>
            </button>
        </div>
    )
}

'use client'

import { useState, useEffect } from 'react'
import { useTheme } from '@/contexts/ThemeContext'

interface BookReaderProps {
    htmlUrl: string
    title: string
}

export default function BookReader({ htmlUrl, title }: BookReaderProps) {
    const { theme } = useTheme()
    const [content, setContent] = useState<string>('')
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [fontSize, setFontSize] = useState(18)

    useEffect(() => {
        async function fetchContent() {
            try {
                setLoading(true)
                const response = await fetch(htmlUrl)
                if (!response.ok) throw new Error('Failed to load book content')
                let html = await response.text()

                // Get the base URL for images from the HTML URL
                const baseUrl = htmlUrl.replace('/result.html', '')

                // Fix ALL image path patterns - works for both old and new books
                // Pattern 1: src="images/xxx.png" or src="./images/xxx.png"
                html = html.replace(/src="\.?\/?(?:images\/[^"]+)"/g, (match) => {
                    const path = match.match(/images\/[^"]+/)?.[0] || ''
                    return `src="${baseUrl}/${path}"`
                })

                // Pattern 2: Absolute local paths like temp_jobs/xxx/output/images/xxx.png
                html = html.replace(/src="[^"]*?(?:temp_jobs|output)[^"]*[\/\\]images[\/\\]([^"]+)"/g, `src="${baseUrl}/images/$1"`)

                // Pattern 3: Windows paths with backslashes
                html = html.replace(/src="[^"]*\\images\\([^"]+)"/g, `src="${baseUrl}/images/$1"`)

                // Pattern 4: Any remaining relative images/ paths
                html = html.replace(/src="(?!https?:\/\/|data:)([^"]*\/)?images\/([^"]+)"/g, `src="${baseUrl}/images/$2"`)

                setContent(html)
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Unknown error')
            } finally {
                setLoading(false)
            }
        }

        if (htmlUrl) {
            fetchContent()
        }
    }, [htmlUrl])

    if (loading) {
        return (
            <div className="flex items-center justify-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-amber-500 border-t-transparent"></div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="text-center py-20">
                <p className="text-red-400">❌ {error}</p>
            </div>
        )
    }

    // Dynamic classes based on theme
    const isDark = theme === 'dark'

    return (
        <div className="relative">
            {/* Font Size Controls */}
            <div className="sticky top-20 z-10 flex justify-end gap-2 mb-4">
                <button
                    onClick={() => setFontSize(s => Math.max(12, s - 2))}
                    className={`px-3 py-1 rounded-lg transition-colors
                              ${isDark
                            ? 'bg-stone-700 hover:bg-stone-600 text-white'
                            : 'bg-amber-200 hover:bg-amber-300 text-amber-900'}`}
                >
                    A-
                </button>
                <span className={`px-3 py-1 rounded-lg
                               ${isDark ? 'bg-stone-800 text-amber-300' : 'bg-amber-100 text-amber-800'}`}>
                    {fontSize}px
                </span>
                <button
                    onClick={() => setFontSize(s => Math.min(32, s + 2))}
                    className={`px-3 py-1 rounded-lg transition-colors
                              ${isDark
                            ? 'bg-stone-700 hover:bg-stone-600 text-white'
                            : 'bg-amber-200 hover:bg-amber-300 text-amber-900'}`}
                >
                    A+
                </button>
            </div>

            {/* Book Content */}
            <article
                className={`prose prose-lg max-w-none transition-colors duration-300
                   ${isDark ? 'prose-invert' : ''}
                   ${isDark
                        ? `[&_*]:!text-amber-100
                        [&_h1]:!text-white [&_h1]:!font-bold [&_h1]:!text-3xl
                        [&_h2]:!text-amber-300 [&_h2]:!font-bold [&_h2]:!text-2xl
                        [&_h3]:!text-amber-200 [&_h3]:!font-semibold
                        [&_p]:!text-amber-100 [&_p]:!leading-relaxed
                        [&_strong]:!text-white [&_em]:!text-amber-200
                        [&_a]:!text-amber-400 [&_a]:!no-underline hover:[&_a]:!underline
                        [&_code]:!text-green-300 [&_code]:!bg-stone-800 [&_code]:!px-2 [&_code]:!py-0.5 [&_code]:!rounded
                        [&_pre]:!bg-stone-800 [&_pre]:!text-amber-100 [&_pre]:!p-4 [&_pre]:!rounded-xl
                        [&_blockquote]:!bg-stone-800/50 [&_blockquote]:!border-l-amber-500 [&_blockquote]:!text-amber-200
                        [&_table]:!bg-stone-800/30 [&_th]:!text-amber-300 [&_th]:!bg-stone-800 [&_td]:!text-amber-100
                        [&_li]:!text-amber-100
                        [&_span]:!text-amber-100`
                        : `[&_*]:!text-stone-800
                        [&_h1]:!text-stone-900 [&_h1]:!font-bold [&_h1]:!text-3xl
                        [&_h2]:!text-amber-800 [&_h2]:!font-bold [&_h2]:!text-2xl
                        [&_h3]:!text-amber-700 [&_h3]:!font-semibold
                        [&_p]:!text-stone-800 [&_p]:!leading-relaxed
                        [&_strong]:!text-stone-900 [&_em]:!text-amber-700
                        [&_a]:!text-amber-600 [&_a]:!no-underline hover:[&_a]:!underline
                        [&_code]:!text-amber-700 [&_code]:!bg-amber-100 [&_code]:!px-2 [&_code]:!py-0.5 [&_code]:!rounded
                        [&_pre]:!bg-amber-100 [&_pre]:!text-stone-800 [&_pre]:!p-4 [&_pre]:!rounded-xl
                        [&_blockquote]:!bg-amber-100/50 [&_blockquote]:!border-l-amber-500 [&_blockquote]:!text-stone-700
                        [&_table]:!bg-amber-100/30 [&_th]:!text-amber-800 [&_th]:!bg-amber-100 [&_td]:!text-stone-800
                        [&_li]:!text-stone-800
                        [&_span]:!text-stone-800`}
                   [&_img]:rounded-xl [&_img]:shadow-lg [&_img]:max-w-full
                   [&_div]:!bg-transparent`}
                style={{ fontSize: `${fontSize}px` }}
                dangerouslySetInnerHTML={{ __html: content }}
            />
        </div>
    )
}

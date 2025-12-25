'use client'

import { useState, useEffect } from 'react'

interface BookReaderProps {
    htmlUrl: string
    title: string
}

export default function BookReader({ htmlUrl, title }: BookReaderProps) {
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

                // Fix image paths - replace relative paths with absolute Supabase URLs
                const baseUrl = htmlUrl.replace('/result.html', '')
                html = html.replace(/src="\.?\/?images\//g, `src="${baseUrl}/images/`)
                html = html.replace(/src="images\//g, `src="${baseUrl}/images/`)

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
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
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

    return (
        <div className="relative">
            {/* Font Size Controls */}
            <div className="sticky top-20 z-10 flex justify-end gap-2 mb-4">
                <button
                    onClick={() => setFontSize(s => Math.max(12, s - 2))}
                    className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors"
                >
                    A-
                </button>
                <span className="px-3 py-1 bg-slate-800 rounded-lg text-slate-300">
                    {fontSize}px
                </span>
                <button
                    onClick={() => setFontSize(s => Math.min(32, s + 2))}
                    className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors"
                >
                    A+
                </button>
            </div>

            {/* Book Content */}
            <article
                className="prose prose-invert prose-lg max-w-none
                   [&_*]:!text-slate-100
                   [&_h1]:!text-white [&_h1]:!font-bold [&_h1]:!text-3xl
                   [&_h2]:!text-purple-300 [&_h2]:!font-bold [&_h2]:!text-2xl
                   [&_h3]:!text-purple-200 [&_h3]:!font-semibold
                   [&_p]:!text-slate-100 [&_p]:!leading-relaxed
                   [&_strong]:!text-white [&_em]:!text-purple-100
                   [&_a]:!text-purple-400 [&_a]:!no-underline hover:[&_a]:!underline
                   [&_img]:rounded-xl [&_img]:shadow-lg [&_img]:max-w-full"
                style={{ fontSize: `${fontSize}px` }}
                dangerouslySetInnerHTML={{ __html: content }}
            />
        </div>
    )
}

'use client'

import { useEffect, useState, useRef } from "react"
import { useTheme } from "@/contexts/ThemeContext"
import { useAuth } from "@/contexts/AuthContext"
import { useRouter } from "next/navigation"
import Link from "next/link"

interface PendingBook {
    id: string
    title: string
    original_title: string | null
    pdf_url: string
    source: string
    category: string
    priority: number
    status: string
    created_at: string
    metadata: Record<string, unknown>
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

const CATEGORIES = [
    { id: 'nlh', name: 'NLH', icon: '♠️' },
    { id: 'omaha', name: 'Omaha', icon: '♥️' },
    { id: 'shortdeck', name: 'Short Deck', icon: '♦️' },
    { id: 'ai_research', name: 'AI/GTO', icon: '🤖' },
    { id: 'psychology', name: 'Tâm lí', icon: '🧠' },
    { id: 'general', name: 'Tổng hợp', icon: '♣️' },
]

export default function QueuePage() {
    const { theme } = useTheme()
    const { user, isAdmin, loading: authLoading } = useAuth()
    const router = useRouter()

    const [pendingBooks, setPendingBooks] = useState<PendingBook[]>([])
    const [loading, setLoading] = useState(true)
    const [uploading, setUploading] = useState(false)
    const [translating, setTranslating] = useState<string | null>(null)
    const [statusFilter, setStatusFilter] = useState('')
    const [sourceFilter, setSourceFilter] = useState('')

    const fileInputRef = useRef<HTMLInputElement>(null)
    const [uploadTitle, setUploadTitle] = useState('')
    const [uploadCategory, setUploadCategory] = useState('general')

    const isDark = theme === 'dark'

    useEffect(() => {
        if (!authLoading && (!user || !isAdmin)) {
            router.push('/admin')
        }
    }, [user, isAdmin, authLoading, router])

    useEffect(() => {
        if (user && isAdmin) {
            loadPendingBooks()
        }
    }, [user, isAdmin])

    const loadPendingBooks = async () => {
        try {
            const params = new URLSearchParams()
            if (statusFilter) params.append('status', statusFilter)
            if (sourceFilter) params.append('source', sourceFilter)
            const queryString = params.toString() ? `?${params.toString()}` : ''

            // Add timeout using AbortController
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), 10000) // 10s timeout

            const response = await fetch(`${API_URL}/api/v1/queue/pending${queryString}`, {
                signal: controller.signal
            })
            clearTimeout(timeoutId)

            if (!response.ok) {
                throw new Error('Failed to fetch')
            }

            const data = await response.json()
            setPendingBooks(data.books || [])
        } catch (error) {
            console.error('Error loading pending books:', error)
            setPendingBooks([])
        } finally {
            setLoading(false)
        }
    }

    // Reload when filters change
    useEffect(() => {
        if (user && isAdmin) {
            loadPendingBooks()
        }
    }, [statusFilter, sourceFilter])

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault()

        const fileInput = fileInputRef.current
        if (!fileInput?.files?.[0]) {
            alert('Vui lòng chọn file PDF')
            return
        }

        const file = fileInput.files[0]
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            alert('Chỉ chấp nhận file PDF')
            return
        }

        setUploading(true)

        try {
            const formData = new FormData()
            formData.append('file', file)
            if (uploadTitle) formData.append('title', uploadTitle)
            formData.append('category', uploadCategory)

            const response = await fetch(`${API_URL}/api/v1/queue/upload`, {
                method: 'POST',
                body: formData
            })

            if (!response.ok) throw new Error('Upload failed')

            const result = await response.json()
            alert(`✅ Đã thêm "${result.title}" vào hàng đợi!`)

            // Reset form
            setUploadTitle('')
            setUploadCategory('general')
            if (fileInputRef.current) fileInputRef.current.value = ''

            // Reload list
            loadPendingBooks()

        } catch (error) {
            alert('❌ Lỗi upload: ' + (error as Error).message)
        } finally {
            setUploading(false)
        }
    }

    const handleTranslate = async (book: PendingBook) => {
        if (!confirm(`Bắt đầu dịch "${book.title}"?`)) return

        setTranslating(book.id)

        try {
            const response = await fetch(`${API_URL}/api/v1/queue/translate/${book.id}`, {
                method: 'POST'
            })

            if (!response.ok) throw new Error('Translation failed to start')

            const result = await response.json()
            alert(`✅ Đang dịch! ID: ${result.translated_book_id}`)

            loadPendingBooks()

        } catch (error) {
            alert('❌ Lỗi: ' + (error as Error).message)
        } finally {
            setTranslating(null)
        }
    }

    const handleDelete = async (book: PendingBook) => {
        if (!confirm(`Xóa "${book.title}" khỏi hàng đợi?`)) return

        try {
            await fetch(`${API_URL}/api/v1/queue/pending/${book.id}`, {
                method: 'DELETE'
            })
            loadPendingBooks()
        } catch (error) {
            alert('Lỗi xóa: ' + (error as Error).message)
        }
    }

    const getStatusBadge = (status: string) => {
        const configs: Record<string, { label: string; color: string }> = {
            pending: { label: 'Chờ dịch', color: 'bg-amber-600' },
            translating: { label: 'Đang dịch', color: 'bg-blue-600' },
            completed: { label: 'Hoàn thành', color: 'bg-green-600' },
            failed: { label: 'Thất bại', color: 'bg-red-600' }
        }
        const config = configs[status] || { label: status, color: 'bg-gray-600' }
        return (
            <span className={`${config.color} text-white text-xs px-2 py-1 rounded-full`}>
                {config.label}
            </span>
        )
    }

    if (authLoading || loading) {
        return (
            <div className={`min-h-screen flex items-center justify-center ${isDark ? 'bg-stone-950' : 'bg-amber-50'}`}>
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-amber-500 border-t-transparent"></div>
            </div>
        )
    }

    if (!user || !isAdmin) {
        return null
    }

    return (
        <div className={`min-h-screen ${isDark ? 'bg-stone-950' : 'bg-amber-50'}`}>
            {/* Header */}
            <div className={`border-b ${isDark ? 'bg-stone-900 border-amber-800/30' : 'bg-white border-amber-200'}`}>
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link href="/admin" className={`text-sm ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                            ← Quay lại Admin
                        </Link>
                        <h1 className={`text-2xl font-bold ${isDark ? 'text-amber-100' : 'text-amber-900'}`}>
                            📚 Hàng Đợi Dịch Sách
                        </h1>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Upload Form */}
                    <div className={`lg:col-span-1 p-6 rounded-xl ${isDark ? 'bg-stone-900' : 'bg-white'} shadow-lg`}>
                        <h2 className={`text-xl font-bold mb-6 ${isDark ? 'text-amber-100' : 'text-amber-900'}`}>
                            📤 Tải Lên PDF
                        </h2>

                        <form onSubmit={handleUpload} className="space-y-4">
                            <div>
                                <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                    File PDF
                                </label>
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    accept=".pdf"
                                    className={`w-full p-3 rounded-lg border ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white'
                                        : 'bg-amber-50 border-amber-200'}`}
                                />
                            </div>

                            <div>
                                <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                    Tên sách (tùy chọn)
                                </label>
                                <input
                                    type="text"
                                    value={uploadTitle}
                                    onChange={(e) => setUploadTitle(e.target.value)}
                                    placeholder="Tự động lấy từ tên file"
                                    className={`w-full p-3 rounded-lg border ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white'
                                        : 'bg-amber-50 border-amber-200'}`}
                                />
                            </div>

                            <div>
                                <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                    Danh mục
                                </label>
                                <select
                                    value={uploadCategory}
                                    onChange={(e) => setUploadCategory(e.target.value)}
                                    className={`w-full p-3 rounded-lg border ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white'
                                        : 'bg-amber-50 border-amber-200'}`}
                                >
                                    {CATEGORIES.map(cat => (
                                        <option key={cat.id} value={cat.id}>
                                            {cat.icon} {cat.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <button
                                type="submit"
                                disabled={uploading}
                                className="w-full py-3 rounded-lg font-semibold bg-amber-600 text-white 
                                         hover:bg-amber-500 disabled:opacity-50 transition-colors"
                            >
                                {uploading ? '⏳ Đang tải...' : '📤 Thêm vào hàng đợi'}
                            </button>
                        </form>
                    </div>

                    {/* Pending Books List */}
                    <div className={`lg:col-span-2 p-6 rounded-xl ${isDark ? 'bg-stone-900' : 'bg-white'} shadow-lg`}>
                        <div className="flex items-center justify-between mb-6">
                            <h2 className={`text-xl font-bold ${isDark ? 'text-amber-100' : 'text-amber-900'}`}>
                                📋 Danh Sách Chờ ({pendingBooks.length})
                            </h2>

                            <div className="flex items-center gap-2">
                                <select
                                    value={sourceFilter}
                                    onChange={(e) => setSourceFilter(e.target.value)}
                                    className={`px-3 py-2 rounded-lg border text-sm ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white'
                                        : 'bg-amber-50 border-amber-200'}`}
                                >
                                    <option value="">📚 Tất cả nguồn</option>
                                    <option value="arxiv">🤖 arXiv</option>
                                    <option value="upload">📤 Admin upload</option>
                                    <option value="user_request">👤 Yêu cầu độc giả</option>
                                </select>

                                <select
                                    value={statusFilter}
                                    onChange={(e) => setStatusFilter(e.target.value)}
                                    className={`px-3 py-2 rounded-lg border text-sm ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white'
                                        : 'bg-amber-50 border-amber-200'}`}
                                >
                                    <option value="">📊 Tất cả trạng thái</option>
                                    <option value="pending">⏳ Chờ dịch</option>
                                    <option value="translating">🔄 Đang dịch</option>
                                    <option value="completed">✅ Hoàn thành</option>
                                    <option value="failed">❌ Thất bại</option>
                                </select>
                            </div>
                        </div>

                        {pendingBooks.length === 0 ? (
                            <div className={`text-center py-12 ${isDark ? 'text-amber-400/60' : 'text-amber-600/60'}`}>
                                <div className="text-4xl mb-4">📭</div>
                                <p>Chưa có sách nào trong hàng đợi</p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {pendingBooks.map(book => (
                                    <div
                                        key={book.id}
                                        className={`p-4 rounded-lg border ${isDark
                                            ? 'bg-stone-800 border-stone-700'
                                            : 'bg-amber-50 border-amber-200'}`}
                                    >
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <h3 className={`font-semibold ${isDark ? 'text-amber-100' : 'text-amber-900'}`}>
                                                        {book.title}
                                                    </h3>
                                                    {getStatusBadge(book.status)}
                                                </div>
                                                <div className={`text-sm ${isDark ? 'text-amber-400/60' : 'text-amber-600/70'}`}>
                                                    <span className={`inline-block px-2 py-0.5 rounded text-xs mr-2 ${book.source === 'arxiv' ? 'bg-purple-500/20 text-purple-400' :
                                                        book.source === 'user_request' ? 'bg-blue-500/20 text-blue-400' :
                                                            'bg-amber-500/20 text-amber-400'
                                                        }`}>
                                                        {book.source === 'arxiv' ? '🤖 arXiv' :
                                                            book.source === 'user_request' ? '👤 Độc giả' :
                                                                '📤 Admin'}
                                                    </span>
                                                    {CATEGORIES.find(c => c.id === book.category)?.icon} {book.category}
                                                    &nbsp;•&nbsp; {new Date(book.created_at).toLocaleDateString('vi-VN')}
                                                    {typeof book.metadata?.note === 'string' && book.metadata.note && (
                                                        <span className="block mt-1 italic">
                                                            💬 "{book.metadata.note.slice(0, 50)}..."
                                                        </span>
                                                    )}
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-2">
                                                {book.status === 'pending' && (
                                                    <button
                                                        onClick={() => handleTranslate(book)}
                                                        disabled={translating === book.id}
                                                        className="px-4 py-2 bg-green-600 text-white rounded-lg 
                                                                 hover:bg-green-500 disabled:opacity-50 text-sm"
                                                    >
                                                        {translating === book.id ? '⏳' : '🌐 Dịch'}
                                                    </button>
                                                )}
                                                <a
                                                    href={book.pdf_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className={`px-4 py-2 rounded-lg text-sm ${isDark
                                                        ? 'bg-stone-700 text-amber-100'
                                                        : 'bg-amber-100 text-amber-800'}`}
                                                >
                                                    📄 PDF
                                                </a>
                                                <button
                                                    onClick={() => handleDelete(book)}
                                                    className="px-3 py-2 text-red-500 hover:text-red-400"
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

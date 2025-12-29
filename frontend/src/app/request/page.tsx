'use client'

import { useState, useRef } from "react"
import { useTheme } from "@/contexts/ThemeContext"
import { useAuth } from "@/contexts/AuthContext"
import Link from "next/link"
import { supabase } from "@/lib/supabase"

const CATEGORIES = [
    { id: 'nlh', name: 'No Limit Hold\'em', icon: '♠️' },
    { id: 'omaha', name: 'Omaha', icon: '♥️' },
    { id: 'shortdeck', name: 'Short Deck', icon: '♦️' },
    { id: 'ai_research', name: 'AI/GTO Research', icon: '🤖' },
    { id: 'psychology', name: 'Tâm lí học', icon: '🧠' },
    { id: 'general', name: 'Tổng hợp', icon: '♣️' },
]

export default function RequestPage() {
    const { theme } = useTheme()
    const { user } = useAuth()

    const [title, setTitle] = useState('')
    const [category, setCategory] = useState('general')
    const [note, setNote] = useState('')
    const [uploading, setUploading] = useState(false)
    const [success, setSuccess] = useState(false)
    const [error, setError] = useState('')

    const fileInputRef = useRef<HTMLInputElement>(null)
    const isDark = theme === 'dark'

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        const file = fileInputRef.current?.files?.[0]
        if (!file) {
            setError('Vui lòng chọn file PDF')
            return
        }

        if (!file.name.toLowerCase().endsWith('.pdf')) {
            setError('Chỉ chấp nhận file PDF')
            return
        }

        setUploading(true)
        setError('')

        try {
            // Generate unique file name
            const fileId = crypto.randomUUID()
            const fileName = `pending/${fileId}.pdf`

            // Upload file to Supabase Storage
            const { error: uploadError } = await supabase.storage
                .from('books')
                .upload(fileName, file)

            if (uploadError) throw uploadError

            // Get public URL
            const { data: urlData } = supabase.storage
                .from('books')
                .getPublicUrl(fileName)

            const pdfUrl = urlData.publicUrl

            // Insert record to pending_books
            const bookTitle = title || file.name.replace('.pdf', '')
            const { error: insertError } = await supabase
                .from('pending_books')
                .insert({
                    id: fileId,
                    title: bookTitle,
                    pdf_url: pdfUrl,
                    source: 'user_request',
                    category: category,
                    priority: 0,  // User requests have lower priority
                    status: 'pending',
                    metadata: note ? { note } : {}
                })

            if (insertError) throw insertError

            setSuccess(true)
            setTitle('')
            setNote('')
            setCategory('general')
            if (fileInputRef.current) fileInputRef.current.value = ''

        } catch (err) {
            setError((err as Error).message)
        } finally {
            setUploading(false)
        }
    }

    return (
        <div className={`min-h-screen pt-24 pb-12 ${isDark ? 'bg-stone-950' : 'bg-amber-50'}`}>
            <div className="max-w-2xl mx-auto px-6">
                {/* Header */}
                <div className="text-center mb-10">
                    <div className="text-5xl mb-4">📚</div>
                    <h1 className={`text-3xl font-bold font-serif mb-3
                                   ${isDark ? 'text-amber-100' : 'text-amber-900'}`}>
                        Yêu Cầu Dịch Sách
                    </h1>
                    <p className={`text-lg ${isDark ? 'text-amber-400/70' : 'text-amber-700'}`}>
                        Gửi sách poker bạn muốn được dịch sang tiếng Việt
                    </p>
                </div>

                {/* Success Message */}
                {success && (
                    <div className="mb-8 p-6 rounded-xl bg-green-500/10 border border-green-500/30 text-center">
                        <div className="text-4xl mb-3">✅</div>
                        <h3 className={`text-xl font-bold mb-2 ${isDark ? 'text-green-400' : 'text-green-600'}`}>
                            Yêu cầu đã được gửi!
                        </h3>
                        <p className={`${isDark ? 'text-green-300/70' : 'text-green-700'}`}>
                            Admin sẽ xem xét và dịch sách của bạn sớm nhất có thể.
                        </p>
                        <button
                            onClick={() => setSuccess(false)}
                            className="mt-4 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-500"
                        >
                            Gửi yêu cầu khác
                        </button>
                    </div>
                )}

                {/* Form */}
                {!success && (
                    <form onSubmit={handleSubmit} className={`p-8 rounded-2xl shadow-xl
                                    ${isDark ? 'bg-stone-900 border border-amber-800/30' : 'bg-white border border-amber-200'}`}>

                        {error && (
                            <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-500">
                                {error}
                            </div>
                        )}

                        {/* File Upload */}
                        <div className="mb-6">
                            <label className={`block text-sm font-medium mb-2
                                             ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                File PDF <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="file"
                                ref={fileInputRef}
                                accept=".pdf"
                                required
                                className={`w-full p-4 rounded-lg border-2 border-dashed cursor-pointer
                                           ${isDark
                                        ? 'bg-stone-800 border-stone-600 text-white hover:border-amber-500'
                                        : 'bg-amber-50 border-amber-300 hover:border-amber-500'}`}
                            />
                            <p className={`mt-2 text-xs ${isDark ? 'text-amber-400/50' : 'text-amber-600/60'}`}>
                                Chỉ chấp nhận file PDF. Kích thước tối đa 50MB.
                            </p>
                        </div>

                        {/* Title */}
                        <div className="mb-6">
                            <label className={`block text-sm font-medium mb-2
                                             ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                Tên sách (tùy chọn)
                            </label>
                            <input
                                type="text"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                placeholder="Để trống sẽ lấy từ tên file"
                                className={`w-full p-4 rounded-lg border
                                           ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white'
                                        : 'bg-amber-50 border-amber-200'}`}
                            />
                        </div>

                        {/* Category */}
                        <div className="mb-6">
                            <label className={`block text-sm font-medium mb-2
                                             ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                Thể loại
                            </label>
                            <select
                                value={category}
                                onChange={(e) => setCategory(e.target.value)}
                                className={`w-full p-4 rounded-lg border
                                           ${isDark
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

                        {/* Note */}
                        <div className="mb-8">
                            <label className={`block text-sm font-medium mb-2
                                             ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                Ghi chú (tùy chọn)
                            </label>
                            <textarea
                                value={note}
                                onChange={(e) => setNote(e.target.value)}
                                placeholder="Ví dụ: Sách rất hay, mong admin dịch sớm..."
                                rows={3}
                                className={`w-full p-4 rounded-lg border resize-none
                                           ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white'
                                        : 'bg-amber-50 border-amber-200'}`}
                            />
                        </div>

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={uploading}
                            className={`w-full py-4 rounded-xl font-bold text-lg transition-all duration-300
                                       hover:shadow-lg disabled:opacity-50
                                       bg-gradient-to-r from-amber-600 to-amber-700 
                                       hover:from-amber-500 hover:to-amber-600 text-white`}
                        >
                            {uploading ? '⏳ Đang tải lên...' : '📤 Gửi Yêu Cầu Dịch'}
                        </button>

                        {/* Info */}
                        <div className={`mt-6 p-4 rounded-lg ${isDark ? 'bg-stone-800' : 'bg-amber-50'}`}>
                            <p className={`text-sm ${isDark ? 'text-amber-400/70' : 'text-amber-700'}`}>
                                💡 <strong>Lưu ý:</strong> Vui lòng chỉ gửi sách poker hợp pháp.
                                Yêu cầu sẽ được admin xem xét và dịch theo thứ tự ưu tiên.
                            </p>
                        </div>
                    </form>
                )}

                {/* Back link */}
                <div className="text-center mt-8">
                    <Link
                        href="/"
                        className={`transition-colors ${isDark ? 'text-amber-400 hover:text-amber-300' : 'text-amber-600 hover:text-amber-700'}`}
                    >
                        ← Về trang chủ
                    </Link>
                </div>
            </div>
        </div>
    )
}

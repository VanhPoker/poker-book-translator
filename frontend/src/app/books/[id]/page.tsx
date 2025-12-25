'use client'

import { useEffect, useState } from "react";
import { getBook, Book } from "@/lib/supabase";
import BookReader from "@/components/BookReader";
import Link from "next/link";
import { useTheme } from "@/contexts/ThemeContext";
import { useParams } from "next/navigation";

export default function BookDetailPage() {
    const params = useParams();
    const id = params.id as string;
    const { theme } = useTheme();
    const [book, setBook] = useState<Book | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadBook() {
            const data = await getBook(id);
            setBook(data);
            setLoading(false);
        }
        if (id) loadBook();
    }, [id]);

    if (loading) {
        return (
            <div className={`min-h-screen flex items-center justify-center ${theme === 'dark' ? 'bg-stone-950' : 'bg-amber-50'}`}>
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-amber-500 border-t-transparent"></div>
            </div>
        );
    }

    if (!book) {
        return (
            <div className={`min-h-screen flex items-center justify-center ${theme === 'dark' ? 'bg-stone-950' : 'bg-amber-50'}`}>
                <div className="text-center">
                    <div className="text-6xl mb-4">📚</div>
                    <p className={`text-xl ${theme === 'dark' ? 'text-amber-300' : 'text-amber-700'}`}>
                        Không tìm thấy sách
                    </p>
                </div>
            </div>
        );
    }

    const formattedDate = book.created_at
        ? new Date(book.created_at).toLocaleDateString("vi-VN", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        })
        : "Chưa xác định";

    const fileSizeMB = book.file_size_bytes
        ? (book.file_size_bytes / 1024 / 1024).toFixed(2)
        : "0";

    return (
        <div className={`min-h-screen transition-colors duration-300 ${theme === 'dark' ? 'bg-stone-950' : 'bg-amber-50'}`}>
            {/* Header Section - Library Style */}
            <section className={`relative py-12 border-b transition-colors duration-300
                              ${theme === 'dark' ? 'border-amber-900/30' : 'border-amber-300/50'}`}>
                <div className={`absolute inset-0 ${theme === 'dark'
                    ? 'bg-gradient-to-br from-amber-950/30 via-stone-950 to-stone-900'
                    : 'bg-gradient-to-br from-amber-100 via-amber-50 to-white'}`}></div>

                <div className="relative max-w-5xl mx-auto px-6">
                    <Link
                        href="/"
                        className={`inline-flex items-center gap-2 transition-colors mb-6 font-serif
                                  ${theme === 'dark' ? 'text-amber-400 hover:text-amber-100' : 'text-amber-700 hover:text-amber-900'}`}
                    >
                        ← Về thư viện
                    </Link>

                    <div className="flex flex-col md:flex-row gap-8 items-start">
                        {/* Book Cover */}
                        <div className={`w-40 h-56 rounded-lg overflow-hidden shadow-2xl flex-shrink-0
                                      ${theme === 'dark'
                                ? 'shadow-amber-900/30 border-2 border-amber-800/30'
                                : 'shadow-amber-300/50 border-2 border-amber-300/50'}`}>
                            {book.cover_url ? (
                                <img
                                    src={book.cover_url}
                                    alt={book.title}
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                <div className={`w-full h-full flex items-center justify-center
                                              ${theme === 'dark'
                                        ? 'bg-gradient-to-br from-amber-700 to-amber-900'
                                        : 'bg-gradient-to-br from-amber-200 to-amber-300'}`}>
                                    <span className="text-5xl">📚</span>
                                </div>
                            )}
                        </div>

                        {/* Book Info */}
                        <div className="flex-1">
                            <h1 className={`font-serif text-3xl md:text-4xl font-bold mb-4
                                          ${theme === 'dark' ? 'text-white' : 'text-amber-900'}`}>
                                {book.title}
                            </h1>

                            <div className={`flex flex-wrap gap-4 text-sm mb-6
                                          ${theme === 'dark' ? 'text-amber-200' : 'text-amber-700'}`}>
                                <span>📅 {formattedDate}</span>
                                <span>💾 {fileSizeMB} MB</span>
                                <span>🌐 {book.target_language?.toUpperCase()}</span>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex flex-wrap gap-4">
                                {book.epub_url && (
                                    <a
                                        href={book.epub_url}
                                        download
                                        className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300
                                                 hover:shadow-lg hover:-translate-y-0.5
                                                 ${theme === 'dark'
                                                ? 'bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white border border-amber-500/30 hover:shadow-amber-500/30'
                                                : 'bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-white hover:shadow-amber-400/30'}`}
                                    >
                                        ⬇️ Tải EPUB
                                    </a>
                                )}
                                {book.pdf_url && (
                                    <a
                                        href={book.pdf_url}
                                        download
                                        className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300
                                                 ${theme === 'dark'
                                                ? 'bg-stone-700 hover:bg-stone-600 text-amber-100 border border-stone-600'
                                                : 'bg-amber-200 hover:bg-amber-300 text-amber-900 border border-amber-300'}`}
                                    >
                                        ⬇️ Tải PDF
                                    </a>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Reader Section */}
            <section className="max-w-4xl mx-auto px-6 py-12">
                {book.status === "completed" && book.html_url ? (
                    <BookReader htmlUrl={book.html_url} title={book.title} />
                ) : book.status === "failed" ? (
                    <div className="text-center py-20">
                        <div className="text-6xl mb-4">❌</div>
                        <p className="text-red-400 text-lg">Dịch sách thất bại</p>
                        <p className={`mt-2 ${theme === 'dark' ? 'text-amber-400/50' : 'text-amber-600/70'}`}>
                            {book.error_message}
                        </p>
                    </div>
                ) : (
                    <div className="text-center py-20">
                        <div className="animate-spin rounded-full h-16 w-16 border-4 border-amber-500 border-t-transparent mx-auto mb-4"></div>
                        <p className={`text-lg ${theme === 'dark' ? 'text-amber-300' : 'text-amber-700'}`}>
                            Đang xử lý sách...
                        </p>
                        <p className={`mt-2 ${theme === 'dark' ? 'text-amber-400/50' : 'text-amber-600/70'}`}>
                            Vui lòng chờ trong giây lát
                        </p>
                    </div>
                )}
            </section>
        </div>
    );
}

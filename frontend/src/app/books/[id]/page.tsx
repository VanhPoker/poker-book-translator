import { getBook } from "@/lib/supabase";
import BookReader from "@/components/BookReader";
import Link from "next/link";
import { notFound } from "next/navigation";

interface PageProps {
    params: Promise<{ id: string }>;
}

export default async function BookDetailPage({ params }: PageProps) {
    const { id } = await params;
    const book = await getBook(id);

    if (!book) {
        notFound();
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
        <div className="min-h-screen">
            {/* Header Section */}
            <section className="relative py-12 border-b border-slate-800">
                <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-transparent to-pink-900/10"></div>

                <div className="relative max-w-5xl mx-auto px-6">
                    <Link
                        href="/"
                        className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-6"
                    >
                        ← Về thư viện
                    </Link>

                    <div className="flex flex-col md:flex-row gap-8 items-start">
                        {/* Book Cover Placeholder */}
                        <div
                            className="w-32 h-44 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 
                          flex items-center justify-center text-5xl shadow-2xl shadow-purple-500/20"
                        >
                            📚
                        </div>

                        {/* Book Info */}
                        <div className="flex-1">
                            <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">
                                {book.title}
                            </h1>

                            <div className="flex flex-wrap gap-4 text-sm text-slate-400 mb-6">
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
                                        className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 
                               hover:from-purple-600 hover:to-pink-600
                               rounded-xl font-semibold text-white transition-all duration-300
                               hover:shadow-lg hover:shadow-purple-500/30 hover:-translate-y-0.5"
                                    >
                                        ⬇️ Tải EPUB
                                    </a>
                                )}
                                {book.pdf_url && (
                                    <a
                                        href={book.pdf_url}
                                        download
                                        className="px-6 py-3 bg-slate-700 hover:bg-slate-600
                               rounded-xl font-semibold text-white transition-all duration-300"
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
                        <p className="text-slate-500 mt-2">{book.error_message}</p>
                    </div>
                ) : (
                    <div className="text-center py-20">
                        <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent mx-auto mb-4"></div>
                        <p className="text-slate-400 text-lg">Đang xử lý sách...</p>
                        <p className="text-slate-500 mt-2">
                            Vui lòng chờ trong giây lát
                        </p>
                    </div>
                )}
            </section>
        </div>
    );
}

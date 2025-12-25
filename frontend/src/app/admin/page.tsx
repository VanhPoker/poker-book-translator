'use client'

import { useEffect, useState, useRef } from "react";
import { supabase, Book, deleteBook } from "@/lib/supabase";
import { useTheme } from "@/contexts/ThemeContext";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";

// Category definitions
const CATEGORIES = [
    { id: 'nlh', name: 'NLH', icon: '♠️' },
    { id: 'omaha', name: 'Omaha', icon: '♥️' },
    { id: 'shortdeck', name: 'Short Deck', icon: '♦️' },
    { id: 'ai_research', name: 'AI/GTO', icon: '🤖' },
    { id: 'psychology', name: 'Tâm lí', icon: '🧠' },
    { id: 'general', name: 'Tổng hợp', icon: '♣️' },
];

export default function AdminPage() {
    const { theme } = useTheme();
    const { user, isAdmin, loading: authLoading, signIn, signOut } = useAuth();
    const [books, setBooks] = useState<Book[]>([]);
    const [loading, setLoading] = useState(true);
    const [showDeleted, setShowDeleted] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loginLoading, setLoginLoading] = useState(false);
    const router = useRouter(); // Initialize useRouter

    // Cover edit state
    const [editingBook, setEditingBook] = useState<Book | null>(null);
    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const isDark = theme === 'dark';

    const handleLogin = async () => {
        setLoginLoading(true);
        setError("");
        const { error } = await signIn(email, password);
        if (error) {
            setError(error.message);
        }
        setLoginLoading(false);
    };

    useEffect(() => {
        async function loadBooks() {
            setLoading(true);
            let query = supabase
                .from('translated_books')
                .select('*')
                .order('created_at', { ascending: false });

            if (!showDeleted) {
                query = query.eq('is_deleted', false);
            }

            const { data, error } = await query;
            if (!error) {
                setBooks(data || []);
            }
            setLoading(false);
        }

        if (user && isAdmin) {
            loadBooks();
        } else if (user && !isAdmin) {
            // If user is logged in but not an admin, redirect to home or sign out
            signOut(); // Sign out the non-admin user
            router.push('/'); // Redirect to home page
        }
    }, [showDeleted, user, isAdmin, router, signOut]);

    const handleDelete = async (id: string, title: string) => {
        if (!confirm(`Xóa sách "${title}"?`)) return;

        const success = await deleteBook(id);
        if (success) {
            if (showDeleted) {
                setBooks(books.map(b =>
                    b.id === id ? { ...b, is_deleted: true } : b
                ));
            } else {
                setBooks(books.filter(b => b.id !== id));
            }
        }
    };

    const handleUpdateCategory = async (id: string, category: string) => {
        const { error } = await supabase
            .from('translated_books')
            .update({ category })
            .eq('id', id);

        if (!error) {
            setBooks(books.map(b =>
                b.id === id ? { ...b, category: category as any } : b
            ));
        }
    };

    const handleRestore = async (id: string) => {
        const { error } = await supabase
            .from('translated_books')
            .update({ is_deleted: false, deleted_at: null })
            .eq('id', id);

        if (!error) {
            setBooks(books.map(b =>
                b.id === id ? { ...b, is_deleted: false } : b
            ));
        }
    };

    const handleCoverUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (!event.target.files || !event.target.files[0] || !editingBook) return;

        const file = event.target.files[0];
        const fileExt = file.name.split('.').pop();
        const fileName = `${editingBook.id}/cover.${fileExt}`;

        setUploading(true);
        try {
            // Upload to Supabase Storage
            const { error: uploadError } = await supabase.storage
                .from('book-assets')
                .upload(fileName, file, { upsert: true });

            if (uploadError) throw uploadError;

            // Get public URL
            const { data: urlData } = supabase.storage
                .from('book-assets')
                .getPublicUrl(fileName);

            // Update book record
            await supabase
                .from('translated_books')
                .update({ cover_url: urlData.publicUrl })
                .eq('id', editingBook.id);

            // Update local state
            setBooks(books.map(b =>
                b.id === editingBook.id ? { ...b, cover_url: urlData.publicUrl } : b
            ));
            setEditingBook(null);
            alert('Cập nhật ảnh bìa thành công!');
        } catch (err) {
            console.error('Error uploading cover:', err);
            alert('Lỗi khi upload ảnh: ' + (err as Error).message);
        } finally {
            setUploading(false);
        }
    };

    // Loading state
    if (authLoading) {
        return (
            <div className={`min-h-screen flex items-center justify-center ${isDark ? 'bg-stone-950' : 'bg-amber-50'}`}>
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-amber-500 border-t-transparent"></div>
            </div>
        );
    }

    // Not logged in - show login form
    if (!user) {
        return (
            <div className={`min-h-screen flex items-center justify-center ${isDark ? 'bg-stone-950' : 'bg-amber-50'}`}>
                <div className={`p-8 rounded-xl shadow-xl max-w-md w-full mx-4
                              ${isDark
                        ? 'bg-stone-900 border border-amber-900/30'
                        : 'bg-white border border-amber-200'}`}>
                    <div className="text-center mb-6">
                        <img src="/logo.png" alt="Admin" className="w-16 h-16 mx-auto" />
                        <h1 className={`font-serif text-2xl font-bold mt-2 ${isDark ? 'text-amber-100' : 'text-amber-900'}`}>
                            Admin Panel
                        </h1>
                        <p className={`text-sm mt-1 ${isDark ? 'text-amber-400/60' : 'text-amber-600/70'}`}>
                            Chỉ dành cho Admin
                        </p>
                    </div>

                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className={`w-full px-4 py-3 rounded-lg mb-3 outline-none
                                  ${isDark
                                ? 'bg-stone-800 border border-stone-700 text-amber-100 focus:border-amber-500'
                                : 'bg-amber-50 border border-amber-200 text-amber-900 focus:border-amber-500'}`}
                    />

                    <input
                        type="password"
                        placeholder="Mật khẩu"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
                        className={`w-full px-4 py-3 rounded-lg mb-4 outline-none
                                  ${isDark
                                ? 'bg-stone-800 border border-stone-700 text-amber-100 focus:border-amber-500'
                                : 'bg-amber-50 border border-amber-200 text-amber-900 focus:border-amber-500'}`}
                    />

                    {error && (
                        <p className="text-red-400 text-sm mb-4">{error}</p>
                    )}

                    <button
                        onClick={handleLogin}
                        disabled={loginLoading}
                        className={`w-full py-3 rounded-lg font-semibold transition-colors
                                  ${loginLoading ? 'opacity-50 cursor-not-allowed' : ''}
                                  ${isDark
                                ? 'bg-amber-600 hover:bg-amber-500 text-white'
                                : 'bg-amber-500 hover:bg-amber-400 text-white'}`}
                    >
                        {loginLoading ? 'Đang đăng nhập...' : 'Đăng nhập'}
                    </button>

                    <Link href="/" className={`block text-center mt-4 text-sm ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                        ← Về trang chủ
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'bg-stone-950' : 'bg-amber-50'}`}>
            {/* Cover Edit Modal */}
            {editingBook && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className={`p-6 rounded-xl max-w-md w-full mx-4 ${isDark ? 'bg-stone-900' : 'bg-white'}`}>
                        <h3 className={`font-serif text-xl font-bold mb-4 ${isDark ? 'text-amber-100' : 'text-amber-900'}`}>
                            Chỉnh sửa ảnh bìa
                        </h3>
                        <p className={`text-sm mb-4 ${isDark ? 'text-amber-300/70' : 'text-amber-700'}`}>
                            {editingBook.title}
                        </p>

                        {/* Current cover preview */}
                        <div className="mb-4">
                            {editingBook.cover_url ? (
                                <img
                                    src={editingBook.cover_url}
                                    alt="Current cover"
                                    className="w-32 h-44 object-cover rounded-lg mx-auto"
                                />
                            ) : (
                                <div className={`w-32 h-44 mx-auto rounded-lg flex items-center justify-center
                                              ${isDark ? 'bg-stone-800' : 'bg-amber-100'}`}>
                                    <span className="text-4xl">📚</span>
                                </div>
                            )}
                        </div>

                        <input
                            type="file"
                            ref={fileInputRef}
                            accept="image/*"
                            onChange={handleCoverUpload}
                            className="hidden"
                        />

                        {/* URL Input Option */}
                        <div className="mb-4">
                            <label className={`block text-sm mb-2 ${isDark ? 'text-amber-300/70' : 'text-amber-700'}`}>
                                Hoặc dán URL ảnh:
                            </label>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    id="cover-url-input"
                                    placeholder="https://example.com/image.jpg"
                                    className={`flex-1 px-3 py-2 rounded-lg text-sm outline-none
                                              ${isDark
                                            ? 'bg-stone-800 border border-stone-700 text-amber-100 focus:border-amber-500'
                                            : 'bg-amber-50 border border-amber-200 text-amber-900 focus:border-amber-500'}`}
                                />
                                <button
                                    onClick={async () => {
                                        const input = document.getElementById('cover-url-input') as HTMLInputElement;
                                        const url = input?.value?.trim();
                                        if (!url || !editingBook) return;

                                        setUploading(true);
                                        try {
                                            const { error } = await supabase
                                                .from('translated_books')
                                                .update({ cover_url: url })
                                                .eq('id', editingBook.id);

                                            if (error) throw error;

                                            setBooks(books.map(b =>
                                                b.id === editingBook.id ? { ...b, cover_url: url } : b
                                            ));
                                            setEditingBook(null);
                                            alert('Cập nhật ảnh bìa thành công!');
                                        } catch (err) {
                                            alert('Lỗi: ' + (err as Error).message);
                                        } finally {
                                            setUploading(false);
                                        }
                                    }}
                                    disabled={uploading}
                                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors
                                              ${isDark
                                            ? 'bg-blue-600 hover:bg-blue-500 text-white'
                                            : 'bg-blue-500 hover:bg-blue-400 text-white'}`}
                                >
                                    🔗 Lưu URL
                                </button>
                            </div>
                        </div>

                        <div className="border-t border-stone-700/30 pt-4 mt-2">
                            <p className={`text-xs mb-3 ${isDark ? 'text-amber-400/50' : 'text-amber-600/60'}`}>
                                Hoặc upload file từ máy:
                            </p>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    disabled={uploading}
                                    className={`flex-1 py-2 rounded-lg font-semibold transition-colors
                                              ${uploading ? 'opacity-50' : ''}
                                              ${isDark
                                            ? 'bg-amber-600 hover:bg-amber-500 text-white'
                                            : 'bg-amber-500 hover:bg-amber-400 text-white'}`}>
                                    {uploading ? '⏳ Đang upload...' : '📷 Chọn file ảnh'}
                                </button>
                                <button
                                    onClick={() => setEditingBook(null)}
                                    className={`px-4 py-2 rounded-lg transition-colors
                                              ${isDark
                                            ? 'bg-stone-700 hover:bg-stone-600 text-amber-100'
                                            : 'bg-amber-100 hover:bg-amber-200 text-amber-900'}`}
                                >
                                    Hủy
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Header */}
            <section className={`py-8 border-b ${isDark ? 'border-amber-900/30' : 'border-amber-300/50'}`}>
                <div className="max-w-6xl mx-auto px-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <span className="text-3xl">⚙️</span>
                            <div>
                                <h1 className={`font-serif text-2xl font-bold ${isDark ? 'text-amber-100' : 'text-amber-900'}`}>
                                    Admin Panel
                                </h1>
                                <p className={`text-sm ${isDark ? 'text-amber-400/60' : 'text-amber-600/70'}`}>
                                    {user.email}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => setShowDeleted(!showDeleted)}
                                className={`px-4 py-2 rounded-lg text-sm transition-colors
                                          ${showDeleted
                                        ? (isDark ? 'bg-red-900/50 text-red-300' : 'bg-red-100 text-red-700')
                                        : (isDark ? 'bg-stone-800 text-amber-300' : 'bg-amber-100 text-amber-700')}`}
                            >
                                {showDeleted ? '🗑️ Đang xem đã xóa' : '📚 Xem sách đã xóa'}
                            </button>

                            <button
                                onClick={signOut}
                                className={`px-4 py-2 rounded-lg text-sm ${isDark ? 'text-amber-400' : 'text-amber-600'}`}
                            >
                                Đăng xuất
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Books Table */}
            <section className="max-w-6xl mx-auto px-6 py-8">
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <div className="animate-spin rounded-full h-12 w-12 border-4 border-amber-500 border-t-transparent"></div>
                    </div>
                ) : books.length === 0 ? (
                    <div className="text-center py-20">
                        <span className="text-6xl">📚</span>
                        <p className={`mt-4 ${isDark ? 'text-amber-300' : 'text-amber-700'}`}>
                            {showDeleted ? 'Không có sách đã xóa' : 'Chưa có sách nào'}
                        </p>
                    </div>
                ) : (
                    <div className={`rounded-xl overflow-hidden border
                                  ${isDark ? 'border-amber-900/30' : 'border-amber-200'}`}>
                        <table className="w-full">
                            <thead className={isDark ? 'bg-stone-900' : 'bg-amber-100'}>
                                <tr>
                                    <th className={`px-4 py-3 text-left font-serif ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                        Bìa
                                    </th>
                                    <th className={`px-4 py-3 text-left font-serif ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                        Tên sách
                                    </th>
                                    <th className={`px-4 py-3 text-left font-serif ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                        Trạng thái
                                    </th>
                                    <th className={`px-4 py-3 text-left font-serif ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                        Danh mục
                                    </th>
                                    <th className={`px-4 py-3 text-left font-serif ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                        Ngày tạo
                                    </th>
                                    <th className={`px-4 py-3 text-right font-serif ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                        Hành động
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {books.map((book) => (
                                    <tr
                                        key={book.id}
                                        className={`border-t ${isDark ? 'border-stone-800' : 'border-amber-100'}
                                                  ${book.is_deleted ? 'opacity-50' : ''}
                                                  ${isDark ? 'hover:bg-stone-900/50' : 'hover:bg-amber-50'}`}
                                    >
                                        <td className="px-4 py-3">
                                            <div
                                                onClick={() => setEditingBook(book)}
                                                className="w-12 h-16 rounded overflow-hidden cursor-pointer hover:ring-2 hover:ring-amber-500 transition-all"
                                            >
                                                {book.cover_url ? (
                                                    <img src={book.cover_url} alt="" className="w-full h-full object-cover" />
                                                ) : (
                                                    <div className={`w-full h-full flex items-center justify-center text-lg
                                                                  ${isDark ? 'bg-stone-800' : 'bg-amber-100'}`}>
                                                        📚
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td className={`px-4 py-3 ${isDark ? 'text-amber-100' : 'text-amber-900'}`}>
                                            <Link href={`/books/${book.id}`} className="hover:underline">
                                                {book.title}
                                            </Link>
                                            {book.is_deleted && (
                                                <span className="ml-2 text-xs text-red-400">(đã xóa)</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 rounded text-xs
                                                          ${book.status === 'completed'
                                                    ? 'bg-green-600 text-white'
                                                    : book.status === 'failed'
                                                        ? 'bg-red-600 text-white'
                                                        : 'bg-amber-600 text-white'}`}>
                                                {book.status}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <select
                                                value={book.category || 'general'}
                                                onChange={(e) => handleUpdateCategory(book.id, e.target.value)}
                                                className={`px-2 py-1 rounded text-sm cursor-pointer
                                                          ${isDark
                                                        ? 'bg-stone-800 border border-stone-700 text-amber-100'
                                                        : 'bg-amber-50 border border-amber-200 text-amber-900'}`}
                                            >
                                                {CATEGORIES.map(cat => (
                                                    <option key={cat.id} value={cat.id}>
                                                        {cat.icon} {cat.name}
                                                    </option>
                                                ))}
                                            </select>
                                        </td>
                                        <td className={`px-4 py-3 text-sm ${isDark ? 'text-amber-300/60' : 'text-amber-600/70'}`}>
                                            {book.created_at
                                                ? new Date(book.created_at).toLocaleDateString('vi-VN')
                                                : '-'}
                                        </td>
                                        <td className="px-4 py-3 text-right space-x-2">
                                            <button
                                                onClick={() => setEditingBook(book)}
                                                className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded transition-colors"
                                            >
                                                📷 Sửa bìa
                                            </button>
                                            {book.is_deleted ? (
                                                <button
                                                    onClick={() => handleRestore(book.id)}
                                                    className="px-3 py-1 text-sm bg-green-600 hover:bg-green-500 text-white rounded transition-colors"
                                                >
                                                    ♻️ Khôi phục
                                                </button>
                                            ) : (
                                                <button
                                                    onClick={() => handleDelete(book.id, book.title)}
                                                    className="px-3 py-1 text-sm bg-red-600 hover:bg-red-500 text-white rounded transition-colors"
                                                >
                                                    🗑️ Xóa
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Stats */}
                <div className={`mt-6 text-sm ${isDark ? 'text-amber-400/60' : 'text-amber-600/70'}`}>
                    Tổng: {books.length} sách
                    {showDeleted && ` (bao gồm ${books.filter(b => b.is_deleted).length} đã xóa)`}
                </div>
            </section>
        </div>
    );
}

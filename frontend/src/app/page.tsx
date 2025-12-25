'use client'

import { useTheme } from "@/contexts/ThemeContext";
import BookCard from "@/components/BookCard";
import SearchBar from "@/components/SearchBar";
import { getBooks, Book } from "@/lib/supabase";
import { useEffect, useState, useCallback } from "react";

// Category definitions
const CATEGORIES = [
  { id: 'all', name: 'Tất cả', icon: '📚' },
  { id: 'nlh', name: 'NLH', icon: '♠️' },
  { id: 'omaha', name: 'Omaha', icon: '♥️' },
  { id: 'shortdeck', name: 'Short Deck', icon: '♦️' },
  { id: 'ai_research', name: 'AI/GTO', icon: '🤖' },
  { id: 'psychology', name: 'Tâm lí', icon: '🧠' },
  { id: 'general', name: 'Tổng hợp', icon: '♣️' },
];

export default function HomePage() {
  const { theme } = useTheme();
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadBooks() {
      try {
        // Timeout after 10 seconds
        const timeoutPromise = new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error('Request timeout')), 10000)
        );

        const data = await Promise.race([getBooks(), timeoutPromise]);
        setBooks(data);
      } catch (err) {
        console.error('Error loading books:', err);
        setError('Không thể tải sách. Vui lòng thử lại sau.');
      } finally {
        setLoading(false);
      }
    }
    loadBooks();
  }, []);

  // Handle search with useCallback to avoid re-renders
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query.toLowerCase());
  }, []);

  // Filter books by category AND search query
  const filteredBooks = books.filter(book => {
    const matchesCategory = selectedCategory === 'all' || book.category === selectedCategory;
    const matchesSearch = !searchQuery || book.title.toLowerCase().includes(searchQuery);
    return matchesCategory && matchesSearch;
  });

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${theme === 'dark' ? 'bg-stone-950' : 'bg-amber-50'}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-amber-500 border-t-transparent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${theme === 'dark' ? 'bg-stone-950' : 'bg-amber-50'}`}>
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <p className={`text-xl mb-4 ${theme === 'dark' ? 'text-amber-300' : 'text-amber-700'}`}>
            {error}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-500"
          >
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${theme === 'dark' ? 'bg-stone-950' : 'bg-amber-50'}`}>
      {/* Hero Section - Library Style */}
      <section className={`relative py-16 overflow-hidden border-b transition-colors duration-300
                          ${theme === 'dark' ? 'border-amber-900/30' : 'border-amber-300/50'}`}>
        {/* Background texture */}
        <div className={`absolute inset-0 ${theme === 'dark'
          ? 'bg-gradient-to-br from-amber-950/30 via-stone-950 to-stone-900'
          : 'bg-gradient-to-br from-amber-100 via-amber-50 to-white'}`}></div>

        <div className="relative max-w-7xl mx-auto px-6 text-center">
          {/* Library Logo */}
          <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full border-4 shadow-2xl mb-6 overflow-hidden
                         ${theme === 'dark'
              ? 'bg-white border-amber-600/50 shadow-amber-900/50'
              : 'bg-white border-amber-400/50 shadow-amber-300/50'}`}>
            <img src="/logo.png" alt="Thư Viện Poker" className="w-20 h-20 object-contain" />
          </div>

          <h1 className={`font-serif text-4xl md:text-5xl font-bold mb-4
                         ${theme === 'dark' ? 'text-amber-100' : 'text-amber-900'}`}>
            Thư Viện Poker
          </h1>
          <p className={`text-xl max-w-2xl mx-auto font-serif italic
                        ${theme === 'dark' ? 'text-amber-300/70' : 'text-amber-700/80'}`}>
            Tàng kinh các poker cho cộng đồng          </p>

          {/* Decorative line */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <div className={`h-px w-16 ${theme === 'dark' ? 'bg-gradient-to-r from-transparent to-amber-600' : 'bg-gradient-to-r from-transparent to-amber-400'}`}></div>
            <span className={theme === 'dark' ? 'text-amber-500' : 'text-amber-600'}>♠ ♥ ♦ ♣</span>
            <div className={`h-px w-16 ${theme === 'dark' ? 'bg-gradient-to-l from-transparent to-amber-600' : 'bg-gradient-to-l from-transparent to-amber-400'}`}></div>
          </div>

          {/* Search Bar */}
          <div className="mt-8">
            <SearchBar onSearch={handleSearch} placeholder="Tìm kiếm sách poker..." />
          </div>
        </div>
      </section>

      {/* Category Filter Tabs */}
      <section className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex flex-wrap gap-2 justify-center">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300
                        ${selectedCategory === cat.id
                  ? (theme === 'dark'
                    ? 'bg-amber-600 text-white shadow-lg shadow-amber-600/30'
                    : 'bg-amber-500 text-white shadow-lg shadow-amber-500/30')
                  : (theme === 'dark'
                    ? 'bg-stone-800 text-amber-300 hover:bg-stone-700'
                    : 'bg-amber-100 text-amber-700 hover:bg-amber-200')}`}
            >
              <span className="mr-1">{cat.icon}</span>
              {cat.name}
              {cat.id !== 'all' && (
                <span className="ml-1 opacity-60">
                  ({books.filter(b => b.category === cat.id).length})
                </span>
              )}
            </button>
          ))}
        </div>
      </section>

      {/* Book Shelf Section */}
      <section className="max-w-7xl mx-auto px-6 py-6">
        {/* Section Header */}
        <div className={`flex items-center justify-between mb-8 pb-4 border-b
                        ${theme === 'dark' ? 'border-amber-900/30' : 'border-amber-300/50'}`}>
          <div className="flex items-center gap-3">

            <h2 className={` text-2xl font-bold ${theme === 'dark' ? 'text-amber-100' : 'text-amber-900'}`}>
              {selectedCategory === 'all' ? 'Kệ Sách' : CATEGORIES.find(c => c.id === selectedCategory)?.name}
            </h2>
          </div>
          <span className={` ${theme === 'dark' ? 'text-amber-400/60' : 'text-amber-600/70'}`}>
            {filteredBooks.length} quyển
          </span>
        </div>

        {filteredBooks.length === 0 ? (
          <div className={`text-center py-20 rounded-xl border
                          ${theme === 'dark'
              ? 'bg-amber-950/20 border-amber-900/20'
              : 'bg-amber-100/50 border-amber-300/30'}`}>
            <img src="/logo.png" alt="" className="w-24 h-24 mx-auto mb-4 opacity-50" />
            <p className={`text-xl font-serif ${theme === 'dark' ? 'text-amber-300/70' : 'text-amber-700'}`}>
              {selectedCategory === 'all' ? 'Thư viện còn trống' : 'Chưa có sách trong danh mục này'}
            </p>
            <p className={`mt-2 ${theme === 'dark' ? 'text-amber-400/50' : 'text-amber-600/70'}`}>
              Upload PDF để bắt đầu dịch sách
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {filteredBooks.map((book) => (
              <BookCard
                key={book.id}
                id={book.id}
                title={book.title}
                status={book.status}
                coverUrl={book.cover_url}
                createdAt={book.created_at}
                category={book.category}
                viewCount={book.view_count}
              />
            ))}
          </div>
        )}
      </section>

      {/* Footer */}
      <footer className={`border-t py-8 mt-12 ${theme === 'dark' ? 'border-amber-900/30' : 'border-amber-300/50'}`}>
        <div className={`max-w-7xl mx-auto px-6 text-center font-serif text-sm
                        ${theme === 'dark' ? 'text-amber-400/40' : 'text-amber-600/60'}`}>

        </div>
      </footer>
    </div>
  );
}

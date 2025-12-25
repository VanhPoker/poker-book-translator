import BookCard from "@/components/BookCard";
import { getBooks } from "@/lib/supabase";

export const revalidate = 60; // Revalidate every 60 seconds

export default async function HomePage() {
  const books = await getBooks();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-transparent to-pink-900/20"></div>
        <div className="absolute top-20 left-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl"></div>

        <div className="relative max-w-7xl mx-auto px-6 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
              Sách Poker Tiếng Việt
            </span>
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Dịch tự động từ các cuốn sách Poker kinh điển bằng AI.
            Đọc online hoặc tải về EPUB.
          </p>
        </div>
      </section>

      {/* Book List */}
      <section className="max-w-7xl mx-auto px-6 pb-20">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold text-white">Thư viện sách</h2>
          <span className="text-slate-400">{books.length} cuốn</span>
        </div>

        {books.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">📚</div>
            <p className="text-slate-400 text-lg">Chưa có sách nào được dịch.</p>
            <p className="text-slate-500 mt-2">Hãy upload PDF để bắt đầu!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {books.map((book) => (
              <BookCard
                key={book.id}
                id={book.id}
                title={book.title}
                status={book.status}
                createdAt={book.created_at}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

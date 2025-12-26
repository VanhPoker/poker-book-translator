import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
        persistSession: true,
        storageKey: 'poker-library-auth',
        storage: typeof window !== 'undefined' ? window.localStorage : undefined,
        autoRefreshToken: true,
        detectSessionInUrl: true
    }
})

export interface Book {
    id: string
    title: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    source_format: string
    target_language: string
    html_url: string | null
    epub_url: string | null
    pdf_url: string | null
    cover_url: string | null
    file_size_bytes: number
    error_message: string | null
    created_at: string | null
    completed_at: string | null
    is_deleted?: boolean
    deleted_at?: string | null
    category?: 'shortdeck' | 'omaha' | 'nlh' | 'ai_research' | 'psychology' | 'general' | null
    view_count?: number
    rating_avg?: number
    rating_count?: number
}

export async function getBooks(): Promise<Book[]> {
    const { data, error } = await supabase
        .from('translated_books')
        .select('*')
        .eq('is_deleted', false)
        .order('view_count', { ascending: false, nullsFirst: false })
        .order('created_at', { ascending: false })

    if (error) {
        console.error('Error fetching books:', error)
        return []
    }

    return data || []
}

export async function deleteBook(id: string): Promise<boolean> {
    const { error } = await supabase
        .from('translated_books')
        .update({ is_deleted: true, deleted_at: new Date().toISOString() })
        .eq('id', id)

    if (error) {
        console.error('Error deleting book:', error)
        return false
    }

    return true
}

export async function getBook(id: string): Promise<Book | null> {
    const { data, error } = await supabase
        .from('translated_books')
        .select('*')
        .eq('id', id)
        .single()

    if (error) {
        console.error('Error fetching book:', error)
        return null
    }

    return data
}

export async function incrementViewCount(id: string): Promise<void> {
    // Get current view count
    const { data: book } = await supabase
        .from('translated_books')
        .select('view_count')
        .eq('id', id)
        .single()

    const currentCount = book?.view_count || 0

    // Increment view count
    const { error } = await supabase
        .from('translated_books')
        .update({ view_count: currentCount + 1 })
        .eq('id', id)

    if (error) {
        console.error('Error incrementing view count:', error)
    }
}

// Rating functions
export async function submitRating(bookId: string, userId: string, rating: number, review?: string): Promise<boolean> {
    // Upsert rating (insert or update)
    const { error: ratingError } = await supabase
        .from('book_ratings')
        .upsert({
            book_id: bookId,
            user_id: userId,
            rating,
            review: review || null
        }, { onConflict: 'book_id,user_id' })

    if (ratingError) {
        console.error('Error submitting rating:', ratingError)
        return false
    }

    // Recalculate average rating
    const { data: ratings } = await supabase
        .from('book_ratings')
        .select('rating')
        .eq('book_id', bookId)

    if (ratings && ratings.length > 0) {
        const avg = ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length

        await supabase
            .from('translated_books')
            .update({
                rating_avg: Math.round(avg * 10) / 10,
                rating_count: ratings.length
            })
            .eq('id', bookId)
    }

    return true
}

export async function getUserRating(bookId: string, userId: string): Promise<number | null> {
    const { data, error } = await supabase
        .from('book_ratings')
        .select('rating')
        .eq('book_id', bookId)
        .eq('user_id', userId)
        .single()

    if (error || !data) {
        return null
    }

    return data.rating
}

// Wishlist/Favorites functions
export async function addToFavorites(bookId: string, userId: string): Promise<boolean> {
    const { error } = await supabase
        .from('user_favorites')
        .insert({ book_id: bookId, user_id: userId })

    if (error) {
        console.error('Error adding to favorites:', error)
        return false
    }
    return true
}

export async function removeFromFavorites(bookId: string, userId: string): Promise<boolean> {
    const { error } = await supabase
        .from('user_favorites')
        .delete()
        .eq('book_id', bookId)
        .eq('user_id', userId)

    if (error) {
        console.error('Error removing from favorites:', error)
        return false
    }
    return true
}

export async function isFavorite(bookId: string, userId: string): Promise<boolean> {
    const { data, error } = await supabase
        .from('user_favorites')
        .select('id')
        .eq('book_id', bookId)
        .eq('user_id', userId)
        .single()

    return !error && !!data
}

export async function getUserFavorites(userId: string): Promise<Book[]> {
    const { data: favorites, error: favError } = await supabase
        .from('user_favorites')
        .select('book_id')
        .eq('user_id', userId)

    if (favError || !favorites) return []

    const bookIds = favorites.map(f => f.book_id)

    const { data: books, error: booksError } = await supabase
        .from('translated_books')
        .select('*')
        .in('id', bookIds)
        .eq('is_deleted', false)

    if (booksError) return []
    return books || []
}

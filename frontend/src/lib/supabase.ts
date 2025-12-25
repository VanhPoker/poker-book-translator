import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export interface Book {
    id: string
    title: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    source_format: string
    target_language: string
    html_url: string | null
    epub_url: string | null
    pdf_url: string | null
    file_size_bytes: number
    error_message: string | null
    created_at: string | null
    completed_at: string | null
}

export async function getBooks(): Promise<Book[]> {
    const { data, error } = await supabase
        .from('translated_books')
        .select('*')
        .order('created_at', { ascending: false })

    if (error) {
        console.error('Error fetching books:', error)
        return []
    }

    return data || []
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

'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { supabase } from '@/lib/supabase'
import { User, Session } from '@supabase/supabase-js'

interface UserProfile {
    id: string
    username: string | null
    email: string | null
    role: 'admin' | 'user'
    display_name: string | null
    created_at: string
}

interface AuthContextType {
    user: User | null
    profile: UserProfile | null
    session: Session | null
    loading: boolean
    isAdmin: boolean
    signIn: (emailOrUsername: string, password: string) => Promise<{ error: Error | null }>
    signUp: (email: string, password: string, username?: string) => Promise<{ error: Error | null }>
    signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    profile: null,
    session: null,
    loading: true,
    isAdmin: false,
    signIn: async () => ({ error: null }),
    signUp: async () => ({ error: null }),
    signOut: async () => { }
})

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [profile, setProfile] = useState<UserProfile | null>(null)
    const [session, setSession] = useState<Session | null>(null)
    const [loading, setLoading] = useState(true)

    // Fetch user profile from user_profiles table
    const fetchProfile = async (userId: string) => {
        const { data, error } = await supabase
            .from('user_profiles')
            .select('*')
            .eq('id', userId)
            .single()

        if (!error && data) {
            setProfile(data)
        } else {
            setProfile(null)
        }
    }

    useEffect(() => {
        // Get initial session
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session)
            setUser(session?.user ?? null)
            if (session?.user) {
                fetchProfile(session.user.id)
            }
            setLoading(false)
        })

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            async (_event, session) => {
                setSession(session)
                setUser(session?.user ?? null)
                if (session?.user) {
                    await fetchProfile(session.user.id)
                } else {
                    setProfile(null)
                }
                setLoading(false)
            }
        )

        return () => subscription.unsubscribe()
    }, [])

    // Sign in with email or username
    const signIn = async (emailOrUsername: string, password: string) => {
        let email = emailOrUsername

        // If not an email, look up the email by username
        if (!emailOrUsername.includes('@')) {
            const { data: userProfile, error: lookupError } = await supabase
                .from('user_profiles')
                .select('email')
                .eq('username', emailOrUsername)
                .single()

            if (lookupError || !userProfile?.email) {
                return { error: new Error('Không tìm thấy tài khoản với username này') }
            }
            email = userProfile.email
        }

        const { error } = await supabase.auth.signInWithPassword({
            email,
            password
        })
        return { error }
    }

    // Sign up new user
    const signUp = async (email: string, password: string, username?: string) => {
        // Check if username already exists
        if (username) {
            const { data: existing } = await supabase
                .from('user_profiles')
                .select('id')
                .eq('username', username)
                .single()

            if (existing) {
                return { error: new Error('Username đã tồn tại') }
            }
        }

        // Create auth user
        const { data: authData, error: authError } = await supabase.auth.signUp({
            email,
            password
        })

        if (authError) {
            return { error: authError }
        }

        // Create user profile
        if (authData.user) {
            const { error: profileError } = await supabase
                .from('user_profiles')
                .insert({
                    id: authData.user.id,
                    email,
                    username: username || null,
                    role: 'user',
                    display_name: username || email.split('@')[0]
                })

            if (profileError) {
                console.error('Error creating profile:', profileError)
            }
        }

        return { error: null }
    }

    const signOut = async () => {
        await supabase.auth.signOut()
        setProfile(null)
    }

    const isAdmin = profile?.role === 'admin'

    return (
        <AuthContext.Provider value={{ user, profile, session, loading, isAdmin, signIn, signUp, signOut }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    return useContext(AuthContext)
}

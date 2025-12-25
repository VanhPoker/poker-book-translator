'use client'

import { useState } from 'react'
import { useTheme } from '@/contexts/ThemeContext'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function LoginPage() {
    const { theme } = useTheme()
    const { signIn, signUp, user } = useAuth()
    const router = useRouter()

    const [isRegister, setIsRegister] = useState(false)
    const [emailOrUsername, setEmailOrUsername] = useState('')
    const [email, setEmail] = useState('')
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')

    const isDark = theme === 'dark'

    // Redirect if already logged in
    if (user) {
        router.push('/')
        return null
    }

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        const { error } = await signIn(emailOrUsername, password)

        if (error) {
            setError(error.message)
        } else {
            router.push('/')
        }

        setLoading(false)
    }

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        setSuccess('')

        if (password !== confirmPassword) {
            setError('Mật khẩu xác nhận không khớp')
            setLoading(false)
            return
        }

        if (password.length < 6) {
            setError('Mật khẩu phải có ít nhất 6 ký tự')
            setLoading(false)
            return
        }

        const { error } = await signUp(email, password, username || undefined)

        if (error) {
            setError(error.message)
        } else {
            setSuccess('Đăng ký thành công! Vui lòng kiểm tra email để xác nhận tài khoản.')
            setIsRegister(false)
        }

        setLoading(false)
    }

    return (
        <div className={`min-h-screen flex items-center justify-center transition-colors duration-300
                        ${isDark ? 'bg-stone-950' : 'bg-amber-50'}`}>
            <div className={`w-full max-w-md p-8 rounded-2xl shadow-2xl
                            ${isDark
                    ? 'bg-stone-900 border border-amber-800/30'
                    : 'bg-white border border-amber-200'}`}>

                {/* Logo */}
                <div className="text-center mb-8">
                    <img src="/logo.png" alt="Logo" className="w-16 h-16 mx-auto mb-4" />
                    <h1 className={`text-2xl font-bold font-serif
                                   ${isDark ? 'text-amber-100' : 'text-amber-900'}`}>
                        {isRegister ? 'Đăng Ký Tài Khoản' : 'Đăng Nhập'}
                    </h1>
                    <p className={`mt-2 text-sm ${isDark ? 'text-amber-400/60' : 'text-amber-600/80'}`}>
                        {isRegister
                            ? 'Tạo tài khoản để lưu sách yêu thích'
                            : 'Đăng nhập bằng email hoặc username'}
                    </p>
                </div>

                {/* Error/Success Messages */}
                {error && (
                    <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-500 text-sm">
                        {error}
                    </div>
                )}
                {success && (
                    <div className="mb-4 p-3 rounded-lg bg-green-500/10 border border-green-500/30 text-green-500 text-sm">
                        {success}
                    </div>
                )}

                {/* Login Form */}
                {!isRegister ? (
                    <form onSubmit={handleLogin} className="space-y-4">
                        <div>
                            <label className={`block text-sm font-medium mb-2
                                             ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                Email hoặc Username
                            </label>
                            <input
                                type="text"
                                value={emailOrUsername}
                                onChange={(e) => setEmailOrUsername(e.target.value)}
                                required
                                className={`w-full px-4 py-3 rounded-lg border transition-colors
                                           ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white focus:border-amber-500'
                                        : 'bg-amber-50 border-amber-200 text-amber-900 focus:border-amber-500'}`}
                                placeholder="email@example.com hoặc username"
                            />
                        </div>

                        <div>
                            <label className={`block text-sm font-medium mb-2
                                             ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                Mật khẩu
                            </label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className={`w-full px-4 py-3 rounded-lg border transition-colors
                                           ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white focus:border-amber-500'
                                        : 'bg-amber-50 border-amber-200 text-amber-900 focus:border-amber-500'}`}
                                placeholder="••••••••"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-3 rounded-lg font-semibold transition-all duration-300
                                       hover:shadow-lg disabled:opacity-50
                                       bg-gradient-to-r from-amber-600 to-amber-700 
                                       hover:from-amber-500 hover:to-amber-600 text-white`}
                        >
                            {loading ? 'Đang xử lý...' : 'Đăng Nhập'}
                        </button>
                    </form>
                ) : (
                    /* Register Form */
                    <form onSubmit={handleRegister} className="space-y-4">
                        <div>
                            <label className={`block text-sm font-medium mb-2
                                             ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                Email <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className={`w-full px-4 py-3 rounded-lg border transition-colors
                                           ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white focus:border-amber-500'
                                        : 'bg-amber-50 border-amber-200 text-amber-900 focus:border-amber-500'}`}
                                placeholder="email@example.com"
                            />
                        </div>

                        <div>
                            <label className={`block text-sm font-medium mb-2
                                             ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                Username <span className={`text-xs ${isDark ? 'text-amber-400/60' : 'text-amber-600'}`}>(tùy chọn)</span>
                            </label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className={`w-full px-4 py-3 rounded-lg border transition-colors
                                           ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white focus:border-amber-500'
                                        : 'bg-amber-50 border-amber-200 text-amber-900 focus:border-amber-500'}`}
                                placeholder="pokerfan123"
                            />
                        </div>

                        <div>
                            <label className={`block text-sm font-medium mb-2
                                             ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                Mật khẩu <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className={`w-full px-4 py-3 rounded-lg border transition-colors
                                           ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white focus:border-amber-500'
                                        : 'bg-amber-50 border-amber-200 text-amber-900 focus:border-amber-500'}`}
                                placeholder="Ít nhất 6 ký tự"
                            />
                        </div>

                        <div>
                            <label className={`block text-sm font-medium mb-2
                                             ${isDark ? 'text-amber-200' : 'text-amber-800'}`}>
                                Xác nhận mật khẩu <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                className={`w-full px-4 py-3 rounded-lg border transition-colors
                                           ${isDark
                                        ? 'bg-stone-800 border-stone-700 text-white focus:border-amber-500'
                                        : 'bg-amber-50 border-amber-200 text-amber-900 focus:border-amber-500'}`}
                                placeholder="Nhập lại mật khẩu"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-3 rounded-lg font-semibold transition-all duration-300
                                       hover:shadow-lg disabled:opacity-50
                                       bg-gradient-to-r from-amber-600 to-amber-700 
                                       hover:from-amber-500 hover:to-amber-600 text-white`}
                        >
                            {loading ? 'Đang xử lý...' : 'Đăng Ký'}
                        </button>
                    </form>
                )}

                {/* Toggle Login/Register */}
                <div className="mt-6 text-center">
                    <button
                        onClick={() => {
                            setIsRegister(!isRegister)
                            setError('')
                            setSuccess('')
                        }}
                        className={`text-sm transition-colors
                                   ${isDark ? 'text-amber-400 hover:text-amber-300' : 'text-amber-600 hover:text-amber-700'}`}
                    >
                        {isRegister
                            ? 'Đã có tài khoản? Đăng nhập'
                            : 'Chưa có tài khoản? Đăng ký ngay'}
                    </button>
                </div>

                {/* Back to Home */}
                <div className="mt-4 text-center">
                    <Link
                        href="/"
                        className={`text-sm transition-colors
                                   ${isDark ? 'text-amber-400/60 hover:text-amber-300' : 'text-amber-500 hover:text-amber-600'}`}
                    >
                        ← Về trang chủ
                    </Link>
                </div>
            </div>
        </div>
    )
}

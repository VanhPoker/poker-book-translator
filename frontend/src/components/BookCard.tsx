interface BookCardProps {
    id: string
    title: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    createdAt: string | null
}

const statusColors = {
    pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    processing: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    completed: 'bg-green-500/20 text-green-400 border-green-500/30',
    failed: 'bg-red-500/20 text-red-400 border-red-500/30',
}

const statusLabels = {
    pending: 'Đang chờ',
    processing: 'Đang dịch',
    completed: 'Hoàn thành',
    failed: 'Lỗi',
}

export default function BookCard({ id, title, status, createdAt }: BookCardProps) {
    const formattedDate = createdAt
        ? new Date(createdAt).toLocaleDateString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        })
        : 'Chưa xác định'

    return (
        <a
            href={`/books/${id}`}
            className="group block p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 
                 rounded-2xl border border-slate-700/50 hover:border-purple-500/50 
                 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/10
                 hover:-translate-y-1"
        >
            <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 
                        flex items-center justify-center text-white text-xl font-bold
                        group-hover:scale-110 transition-transform duration-300">
                    📚
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${statusColors[status]}`}>
                    {statusLabels[status]}
                </span>
            </div>

            <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2 group-hover:text-purple-300 transition-colors">
                {title}
            </h3>

            <p className="text-sm text-slate-400">
                {formattedDate}
            </p>
        </a>
    )
}

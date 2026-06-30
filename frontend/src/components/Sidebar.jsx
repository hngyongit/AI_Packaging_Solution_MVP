import React from 'react'
import { Plus, Trash2, MessageCircle, Package } from 'lucide-react'

export default function Sidebar({ conversations, activeId, onSelect, onNew, onDelete }) {
    return (
        <aside className="w-72 bg-pearl-100 border-r border-carton-200 flex flex-col shrink-0">
            <div className="p-4 border-b border-carton-200">
                <div className="flex items-center gap-2.5 mb-4">
                    <div className="w-9 h-9 bg-carton-500 flex items-center justify-center">
                        <Package className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h2 className="text-base font-bold text-carton-900 leading-tight">Bao bì AI</h2>
                        <p className="text-[11px] text-carton-600 font-medium tracking-wide">Giải pháp</p>
                    </div>
                </div>
                <button
                    onClick={onNew}
                    className="w-full flex items-center justify-center gap-2 bg-carton-500 hover:bg-carton-600 text-white py-2.5 text-sm font-semibold transition"
                >
                    <Plus className="w-4 h-4" />
                    Trò chuyện mới
                </button>
            </div>

            <div className="flex-1 flex flex-col min-h-0">
                <div className="px-5 pt-3 pb-1.5">
                    <p className="text-[10px] font-semibold text-carton-600 uppercase tracking-wider">Cuộc trò chuyện</p>
                </div>

                <nav className="flex-1 overflow-y-auto px-2 pb-2 space-y-0.5">
                    {conversations.length === 0 && (
                        <p className="text-xs text-carton-500 text-center pt-6 px-3">
                            Chưa có cuộc trò chuyện nào. Hãy bắt đầu một cuộc trò chuyện mới.
                        </p>
                    )}
                    {conversations.map(conv => (
                        <div
                            key={conv.id}
                            onClick={() => onSelect(conv.id)}
                            className={`group flex items-center gap-2 px-3 py-2.5 cursor-pointer text-sm transition ${activeId === conv.id
                                    ? 'bg-carton-200 text-carton-900 font-medium'
                                    : 'text-carton-700 hover:bg-carton-100'
                                }`}
                        >
                            <MessageCircle className="w-4 h-4 shrink-0" />
                            <span className="truncate flex-1">{conv.title || 'Chưa có tiêu đề'}</span>
                            <button
                                onClick={e => { e.stopPropagation(); onDelete(conv.id) }}
                                className="opacity-0 group-hover:opacity-100 hover:text-red-600 transition p-0.5"
                                title="Xóa cuộc trò chuyện"
                            >
                                <Trash2 className="w-3.5 h-3.5" />
                            </button>
                        </div>
                    ))}
                </nav>
            </div>

            <div className="p-3 border-t border-carton-200 bg-pearl-100">
                <div className="flex items-center gap-2 px-2">
                    <div className="w-6 h-6 bg-carton-300 flex items-center justify-center">
                        <Package className="w-3.5 h-3.5 text-carton-700" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-[11px] font-medium text-carton-800 truncate">
                            Giải pháp Bao bì AI
                        </p>
                        <p className="text-[10px] text-carton-600">
                            Thiết kế và tối ưu hóa thùng carton
                        </p>
                    </div>
                </div>
            </div>
        </aside>
    )
}

import React from 'react'
import { Plus, Trash2, MessageCircle, Box } from 'lucide-react'

export default function Sidebar({ conversations, activeId, onSelect, onNew, onDelete }) {
    return (
        <aside className="w-72 bg-white border-r border-slate-200 flex flex-col shrink-0">
            {/* Brand + New chat */}
            <div className="p-4 border-b border-slate-100">
                <div className="flex items-center gap-2.5 mb-3">
                    <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-sm">
                        <Box className="w-4 h-4 text-white" />
                    </div>
                    <div>
                        <h2 className="text-sm font-bold text-slate-800 leading-tight">AI Packaging</h2>
                        <p className="text-[10px] text-slate-400 font-medium tracking-wide">Solution</p>
                    </div>
                </div>
                <button
                    onClick={onNew}
                    className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white py-2.5 text-sm font-semibold shadow-sm hover:shadow-md transition-all"
                >
                    <Plus className="w-4 h-4" />
                    New Chat
                </button>
            </div>

            {/* Section label */}
            <div className="px-5 pt-3 pb-1">
                <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Conversations</p>
            </div>

            {/* Conversations list */}
            <nav className="flex-1 overflow-y-auto px-2 pb-2 space-y-0.5">
                {conversations.length === 0 && (
                    <p className="text-xs text-slate-400 text-center pt-6">No conversations yet</p>
                )}
                {conversations.map(conv => (
                    <div
                        key={conv.id}
                        onClick={() => onSelect(conv.id)}
                        className={`group flex items-center gap-2 px-3 py-2.5 rounded-xl cursor-pointer text-sm transition-all ${activeId === conv.id
                                ? 'bg-emerald-50 text-emerald-700 font-medium shadow-sm'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800'
                            }`}
                    >
                        <MessageCircle className="w-4 h-4 shrink-0" />
                        <span className="truncate flex-1">{conv.title || 'Untitled'}</span>
                        <button
                            onClick={e => { e.stopPropagation(); onDelete(conv.id) }}
                            className="opacity-0 group-hover:opacity-100 hover:text-red-500 transition p-0.5"
                            title="Delete"
                        >
                            <Trash2 className="w-3.5 h-3.5" />
                        </button>
                    </div>
                ))}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-slate-100 text-center">
                <span className="text-[10px] text-slate-400">Powered by AI</span>
            </div>
        </aside>
    )
}

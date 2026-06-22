import React from 'react'
import { MessageSquarePlus, Box } from 'lucide-react'

export default function EmptyState({ onNew }) {
    return (
        <div className="flex flex-col items-center justify-center h-full text-center px-6">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center mb-6 shadow-lg shadow-emerald-500/20">
                <Box className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-extrabold text-slate-800 mb-2">
                AI Packaging Solution
            </h2>
            <p className="text-sm text-slate-500 max-w-md mb-2">
                Your intelligent packaging consultant. Ask about carton boxes, pricing, printing, or anything packaging-related.
            </p>
            <p className="text-xs text-slate-400 max-w-sm mb-8">
                Start a conversation and get expert recommendations instantly.
            </p>
            <button
                onClick={onNew}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-br from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white rounded-xl text-sm font-semibold shadow-md hover:shadow-lg transition-all"
            >
                <MessageSquarePlus className="w-4 h-4" />
                Start New Chat
            </button>
        </div>
    )
}

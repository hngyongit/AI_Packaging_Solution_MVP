import React from 'react'
import ReactMarkdown from 'react-markdown'
import { User, AlertTriangle } from 'lucide-react'

export default function ChatMessage({ message }) {
    const isUser = message.role === 'user'
    const isTool = message.role === 'tool'
    const isError = message._error

    return (
        <div className={`flex items-start gap-3 px-4 py-3 animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`}>
            {/* Avatar */}
            {isUser ? (
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-violet-600 flex items-center justify-center shadow-sm shrink-0">
                    <User className="w-4 h-4 text-white" />
                </div>
            ) : isTool ? (
                <div className="w-9 h-9 rounded-xl bg-amber-100 border-2 border-amber-200 flex items-center justify-center shrink-0">
                    <span className="text-base">🔧</span>
                </div>
            ) : (
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center text-xs font-bold text-white shadow-sm shrink-0">
                    AI
                </div>
            )}

            {/* Bubble */}
            <div
                className={`max-w-[75%] rounded-xl px-4 py-2.5 text-sm leading-relaxed ${isUser
                        ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 text-white rounded-br-sm shadow-sm'
                        : isTool
                            ? 'bg-amber-50 border-2 border-amber-200 text-amber-800 rounded-bl-sm font-mono text-xs'
                            : isError
                                ? 'bg-red-50 border-2 border-red-200 text-red-700 rounded-bl-sm'
                                : 'bg-white shadow-sharp border border-slate-100 text-slate-700 rounded-bl-sm'
                    }`}
            >
                {isUser ? (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                ) : (
                    <div className="prose prose-sm max-w-none">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                )}
            </div>

            {/* Error icon */}
            {isError && (
                <AlertTriangle className="w-4 h-4 text-red-400 mt-2 shrink-0" />
            )}
        </div>
    )
}

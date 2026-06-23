import React from 'react'
import ReactMarkdown from 'react-markdown'
import { User, AlertTriangle, Image as ImageIcon } from 'lucide-react'

export default function ChatMessage({ message }) {
    const isUser = message.role === 'user'
    const isTool = message.role === 'tool'
    const isError = message._error || message._mockupError
    const hasMockupProgress = message._progress !== undefined && message._progress < 100 && !message.image_url
    const hasMockupImage = message.image_url && message.image_url.length > 0

    // Strip mockup metadata comments for display
    const displayContent = message.content
        ?.replace(/<!--MOCKUP_PROGRESS task_id=[^ ]+ -->/g, '')
        ?.replace(/<!--MOCKUP task_id=[^ ]+ -->/g, '')
        ?.trim()

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
                            : hasMockupProgress
                                ? 'bg-white shadow-sharp border border-slate-100 text-slate-700 rounded-bl-sm'
                                : 'bg-white shadow-sharp border border-slate-100 text-slate-700 rounded-bl-sm'
                    }`}
            >
                {/* Show progress bar while generating */}
                {hasMockupProgress && (
                    <div className="mb-3">
                        <div className="flex items-center gap-2 mb-2">
                            <ImageIcon className="w-4 h-4 text-emerald-500 animate-pulse" />
                            <span className="font-semibold text-slate-700 text-sm">Generating Mockup</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                            <div
                                className="bg-gradient-to-r from-emerald-400 to-emerald-600 h-full rounded-full animate-pulse"
                                style={{ width: message._progress + '%', transition: 'width 0.5s ease-in-out' }}
                            />
                        </div>
                        <p className="text-xs text-slate-500 mt-1.5">{message._progressText || 'Creating your packaging mockup...'}</p>
                    </div>
                )}

                {/* Show generated image */}
                {hasMockupImage && message.image_url && (
                    <div className="mb-3">
                        <div className="rounded-lg overflow-hidden border border-slate-200 bg-slate-50">
                            <img
                                src={message.image_url}
                                alt="Packaging Mockup"
                                className="w-full h-auto object-contain max-h-80"
                                loading="lazy"
                                onError={(e) => {
                                    e.target.style.display = 'none'
                                    e.target.parentElement.querySelector('.mockup-error')?.classList.remove('hidden')
                                }}
                            />
                            <div className="mockup-error hidden items-center justify-center h-40 text-slate-400 text-sm">
                                <span>Image could not be loaded</span>
                            </div>
                        </div>
                    </div>
                )}

                {isUser ? (
                    <p className="whitespace-pre-wrap">{displayContent}</p>
                ) : (
                    <div className="prose prose-sm max-w-none">
                        <ReactMarkdown>{displayContent || ''}</ReactMarkdown>
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

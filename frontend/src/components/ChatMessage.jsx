import React from 'react'
import ReactMarkdown from 'react-markdown'
import { User, AlertTriangle, Image as ImageIcon, Copy } from 'lucide-react'

export default function ChatMessage({ message }) {
    const isUser = message.role === 'user'
    const isTool = message.role === 'tool'
    const isError = message._error || message._mockupError
    const hasMockupProgress = message._progress !== undefined && message._progress < 100 && !message.image_url
    const hasMockupImage = message.image_url && message.image_url.length > 0

    const displayContent = message.content
        ?.replace(/<!--MOCKUP_PROGRESS task_id=[^ ]+ -->/g, '')
        ?.replace(/<!--MOCKUP task_id=[^ ]+ -->/g, '')
        ?.trim()

    const handleCopy = (text) => {
        navigator.clipboard.writeText(text).then(() => {})
    }

    return (
        <div className={`flex items-start gap-3 px-4 py-3 animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`}>
            {isUser ? (
                <div className="w-9 h-9 bg-carton-500 flex items-center justify-center shrink-0">
                    <User className="w-4 h-4 text-white" />
                </div>
            ) : isTool ? (
                <div className="w-9 h-9 bg-amber-100 border border-amber-300 flex items-center justify-center shrink-0">
                    <span className="text-base">Wrench</span>
                </div>
            ) : (
                <div className="w-9 h-9 bg-carton-500 flex items-center justify-center text-xs font-bold text-white shrink-0">
                    AI
                </div>
            )}

            <div
                className={`max-w-[75%] px-4 py-2.5 text-sm leading-relaxed ${
                    isUser
                        ? 'bg-carton-500 text-white'
                        : isTool
                            ? 'bg-amber-50 border border-amber-300 text-amber-800 font-mono text-xs'
                            : isError
                                ? 'bg-red-50 border border-red-200 text-red-700'
                                : 'bg-pearl-100 border border-carton-200 text-carton-900'
                }`}
            >
                {hasMockupProgress && (
                    <div className="mb-3">
                        <div className="flex items-center gap-2 mb-2">
                            <ImageIcon className="w-4 h-4 text-carton-500" />
                            <span className="font-semibold text-carton-800 text-sm">Generating Mockup</span>
                        </div>
                        <div className="w-full bg-carton-200 h-2 overflow-hidden">
                            <div
                                className="bg-carton-500 h-full"
                                style={{ width: message._progress + '%', transition: 'width 0.3s ease-in-out' }}
                            />
                        </div>
                        <p className="text-xs text-carton-600 mt-1.5">{message._progressText || 'Creating your packaging mockup...'}</p>
                    </div>
                )}

                {hasMockupImage && message.image_url && (
                    <div className="mb-3">
                        <div className="overflow-hidden border border-carton-200 bg-pearl-50">
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
                            <div className="mockup-error hidden items-center justify-center h-40 text-carton-500 text-sm">
                                <span>Image could not be loaded</span>
                            </div>
                        </div>
                        <button
                            onClick={() => handleCopy(message.image_url)}
                            className="mt-2 text-xs text-carton-600 hover:text-carton-700 flex items-center gap-1"
                        >
                            <Copy className="w-3 h-3" />
                            Copy image URL
                        </button>
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

            {isError && (
                <AlertTriangle className="w-4 h-4 text-red-500 mt-2 shrink-0" />
            )}
        </div>
    )
}

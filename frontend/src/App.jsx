import React, { useState, useEffect, useRef, useCallback } from 'react'
import {
    listConversations,
    createConversation,
    deleteConversation,
    getMessages,
    sendMessage,
    updateMockupImage,
    subscribeMockupSSE,
} from './api.js'
import ChatMessage from './components/ChatMessage.jsx'
import Sidebar from './components/Sidebar.jsx'
import EmptyState from './components/EmptyState.jsx'
import { Send, Loader2, Package, MessageCircle } from 'lucide-react'

export default function App() {
    const [conversations, setConversations] = useState([])
    const [activeId, setActiveId] = useState(null)
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [sending, setSending] = useState(false)
    const [loadingMsgs, setLoadingMsgs] = useState(false)
    const activeConv = conversations.find(c => c.id === activeId)
    const messagesEndRef = useRef(null)

    // ── Load conversations ──────────────────────────────────────
    const loadConversations = useCallback(async () => {
        try {
            const list = await listConversations()
            setConversations(list)
        } catch { /* backend may not be ready yet */ }
    }, [])

    useEffect(() => { loadConversations() }, [loadConversations])

    // ── Mockup SSE ──────────────────────────────────────────────
    const sseUnsubscribers = useRef({})

    const startMockupSSE = useCallback((messageId, taskId) => {
        // Avoid duplicate subscriptions
        if (sseUnsubscribers.current[taskId]) return

        // Show progress immediately
        setMessages(prev => prev.map(m =>
            m.id === messageId
                ? { ...m, _progress: 5, _progressText: 'Starting image generation...' }
                : m
        ))

        const unsubscribe = subscribeMockupSSE(taskId, {
            onStatus(data) {
                // status event with progress
                const progress = data.progress ?? 0
                const status = data.status ?? 'PROCESSING'
                setMessages(prev => prev.map(m =>
                    m.id === messageId
                        ? { ...m, _progress: Math.max(5, progress), _progressText: 'Generating your packaging mockup...' }
                        : m
                ))
            },
            onProgress(progress) {
                setMessages(prev => prev.map(m =>
                    m.id === messageId
                        ? { ...m, _progress: Math.max(5, progress), _progressText: 'Generating your packaging mockup...' }
                        : m
                ))
            },
            onComplete(data) {
                if (data.status === 'COMPLETED' && data.result_url) {
                    // Persist to backend and update message
                    updateMockupImage(messageId, data.result_url).catch(() => { })
                    setMessages(prev => prev.map(m =>
                        m.id === messageId
                            ? { ...m, image_url: data.result_url, _progress: undefined, _progressText: undefined }
                            : m
                    ))
                } else {
                    setMessages(prev => prev.map(m =>
                        m.id === messageId
                            ? { ...m, _mockupError: true, content: m.content + '\n\n⚠️ Mockup generation failed.' }
                            : m
                    ))
                }
                delete sseUnsubscribers.current[taskId]
            },
            onError(error) {
                console.warn('Mockup SSE error:', error)
                delete sseUnsubscribers.current[taskId]
            },
        })

        sseUnsubscribers.current[taskId] = unsubscribe
    }, [])

    // Cleanup SSE on unmount
    useEffect(() => {
        return () => {
            Object.values(sseUnsubscribers.current).forEach(fn => fn())
            sseUnsubscribers.current = {}
        }
    }, [])

    // ── Load messages when conversation changes ─────────────────
    useEffect(() => {
        if (!activeId) { setMessages([]); return }
        setLoadingMsgs(true)
        getMessages(activeId)
            .then(msgs => {
                // Check for bot messages that have a mockup_task_id but no image_url yet
                const msgsWithProgress = msgs.map(m => {
                    if (m.role === 'assistant' && m.mockup_task_id && !m.image_url) {
                        return {
                            ...m,
                            _progress: 10,
                            _progressText: 'Resuming image generation...',
                        }
                    }
                    return m
                })
                setMessages(msgsWithProgress)
                // Auto-start SSE for any pending mockups
                for (const m of msgs) {
                    if (m.role === 'assistant' && m.mockup_task_id && !m.image_url) {
                        startMockupSSE(m.id, m.mockup_task_id)
                    }
                }
            })
            .catch(() => setMessages([]))
            .finally(() => setLoadingMsgs(false))
    }, [activeId, startMockupSSE])

    // ── New conversation ────────────────────────────────────────
    const handleNewChat = async () => {
        const conv = await createConversation()
        setConversations(prev => [conv, ...prev])
        setActiveId(conv.id)
    }

    // ── Delete conversation ─────────────────────────────────────
    const handleDelete = async (id) => {
        await deleteConversation(id)
        setConversations(prev => prev.filter(c => c.id !== id))
        if (activeId === id) setActiveId(null)
    }

    // ── Send message ────────────────────────────────────────────
    const handleSend = async () => {
        const text = input.trim()
        if (!text || sending) return
        setInput('')
        setSending(true)

        let convId = activeId
        // Auto-create a conversation if none is active
        if (!convId) {
            const conv = await createConversation(text.slice(0, 60))
            convId = conv.id
            setActiveId(convId)
            setConversations(prev => [conv, ...prev])
        }

        // Optimistic user message (shown immediately)
        const optimisticUser = {
            _optimistic: true,
            id: `tmp-${Date.now()}`,
            conversation_id: convId,
            role: 'user',
            content: text,
        }
        setMessages(prev => [...prev, optimisticUser])

        try {
            const result = await sendMessage(convId, text)

            // Must read bot_message.id before setMessages to avoid stale ref
            const botMsgId = result.bot_message?.id
            const mockupTaskId = result.mockup_task_id

            setMessages(prev => {
                const updated = [
                    ...prev.filter(m => m.id !== optimisticUser.id),
                    result.user_message,
                ]
                if (result.tool_calls?.length) {
                    for (const tc of result.tool_calls) {
                        updated.push({
                            id: `tool-${tc.name}-${Date.now()}`,
                            role: 'tool',
                            content: `🔧 **${tc.name}** called with \`${JSON.stringify(tc.arguments)}\` → ${tc.result}`,
                        })
                    }
                }
                updated.push(result.bot_message)
                return updated
            })

            // Start SSE for mockup (outside updater to avoid nested state calls)
            if (mockupTaskId && botMsgId) {
                startMockupSSE(botMsgId, mockupTaskId)
            }
            // Update active ID if this was a new conversation
            if (!activeId) setActiveId(result.conversation_id)
            loadConversations()
        } catch {
            setMessages(prev => [
                ...prev.filter(m => m.id !== optimisticUser.id),
                optimisticUser,
                { id: `err-${Date.now()}`, role: 'assistant', content: '⚠️ Failed to get response. Is the backend running?', _error: true },
            ])
        } finally {
            setSending(false)
        }
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    // ── Filter out first message if it matches conversation title ──
    const filteredMessages = (() => {
        if (!activeConv || !messages.length) return messages
        const title = activeConv.title
        if (!title || title === 'New Chat' || title === 'Untitled') return messages
        const firstMsg = messages[0]
        if (firstMsg.role === 'user' && firstMsg.content && firstMsg.content.startsWith(title)) {
            return messages.slice(1)
        }
        return messages
    })()

    return (
        <div className="flex h-screen w-screen overflow-hidden bg-pearl-50">
            <Sidebar
                conversations={conversations}
                activeId={activeId}
                onSelect={setActiveId}
                onNew={handleNewChat}
                onDelete={handleDelete}
            />

            <main className="flex-1 flex flex-col min-w-0">
                <header className="flex items-center gap-3 px-6 py-4 bg-pearl-100 border-b border-carton-200 z-10 shrink-0">
                    <div className="w-9 h-9 bg-carton-500 flex items-center justify-center">
                        <Package className="w-5 h-5 text-white" />
                    </div>
                    <div className="min-w-0">
                        <h1 className="text-base font-bold text-carton-900 leading-tight truncate">
                            {activeConv ? activeConv.title : 'AI Packaging Solution'}
                        </h1>
                        <p className="text-[11px] font-medium text-carton-600 tracking-wide">
                            AI Packaging Consultant
                        </p>
                    </div>
                    <div className="ml-auto flex items-center gap-2">
                        <span className="flex items-center gap-1.5 px-3 py-1 bg-carton-100 text-carton-700 text-xs font-medium">
                            <span className="w-1.5 h-1.5 bg-carton-500 inline-block" />
                            Online
                        </span>
                    </div>
                </header>

                <div className="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-6 space-y-2">
                    {!activeId ? (
                        <EmptyState onNew={handleNewChat} />
                    ) : loadingMsgs ? (
                        <div className="flex justify-center py-20">
                            <Loader2 className="w-6 h-6 animate-spin text-carton-400" />
                        </div>
                    ) : filteredMessages.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-carton-400">
                            <MessageCircle className="w-10 h-10 mb-3 text-carton-300" />
                            <p className="text-sm">Send a message to start chatting</p>
                        </div>
                    ) : (
                        filteredMessages.map(m => <ChatMessage key={m.id} message={m} />)
                    )}
                    {sending && (
                        <div className="flex items-start gap-3 px-4 py-3.5 animate-fade-in">
                            <div className="w-9 h-9 bg-carton-500 flex items-center justify-center text-xs font-bold text-white shrink-0">
                                AI
                            </div>
                            <div className="flex items-center gap-1.5 py-2">
                                <span className="w-2 h-2 bg-carton-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                                <span className="w-2 h-2 bg-carton-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                                <span className="w-2 h-2 bg-carton-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="bg-pearl-100 border-t border-carton-200 px-4 sm:px-6 lg:px-8 py-4 shrink-0">
                    <div className="max-w-4xl mx-auto flex gap-3 items-end">
                        <div className="flex-1 relative">
                            <textarea
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask about packaging solutions..."
                                rows={1}
                                className="w-full resize-none bg-pearl-50 border border-carton-300 px-4 py-3 text-sm text-carton-900 placeholder-carton-400 focus:outline-none focus:border-carton-500 transition"
                                style={{ minHeight: 48, maxHeight: 160 }}
                                onInput={e => {
                                    e.target.style.height = 'auto'
                                    e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
                                }}
                            />
                        </div>
                        <button
                            onClick={handleSend}
                            disabled={!input.trim() || sending}
                            className="flex items-center justify-center w-12 h-12 bg-carton-500 hover:bg-carton-600 disabled:bg-carton-200 disabled:text-pearl-300 text-white transition shrink-0"
                        >
                            {sending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                        </button>
                    </div>
                </div>
            </main>
        </div>
    )
}

import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
    headers: { 'Content-Type': 'application/json' },
})

export async function healthCheck() {
    const { data } = await api.get('/api/health')
    return data
}

export async function listConversations() {
    const { data } = await api.get('/api/conversations')
    return data
}

export async function createConversation(title = 'New Chat') {
    const { data } = await api.post('/api/conversations', null, { params: { title } })
    return data
}

export async function deleteConversation(id) {
    await api.delete(`/api/conversations/${id}`)
}

export async function getMessages(conversationId) {
    const { data } = await api.get(`/api/conversations/${conversationId}/messages`)
    return data
}

export async function sendMessage(conversationId, content) {
    const { data } = await api.post('/api/chat', { conversation_id: conversationId, content })
    return data  // { user_message, bot_message, conversation_id, mockup_task_id, tool_calls }
}

export async function getMockupStatus(taskId) {
    const { data } = await api.get(`/api/mockup/status/${taskId}`)
    return data  // { status, image_url, message }
}

export async function updateMockupImage(messageId, imageUrl) {
    const { data } = await api.patch(`/api/mockup/message/${messageId}`, { image_url: imageUrl })
    return data  // { ok: true }
}

/**
 * Subscribe to real-time SSE events for a mockup generation task.
 *
 * @param {string} taskId - The Lumicraft task ID.
 * @param {object} callbacks - { onStatus, onProgress, onComplete, onError }
 * @returns {() => void} - An unsubscribe function to abort the connection.
 */
export function subscribeMockupSSE(taskId, callbacks) {
    const baseUrl = import.meta.env.VITE_API_URL || ''
    const url = `${baseUrl.replace(/\/+$/, '')}/api/mockup/sse/${taskId}`
    const controller = new AbortController()

    const connect = () => {
        fetch(url, {
            signal: controller.signal,
            headers: { Accept: 'text/event-stream' },
        })
            .then(async (response) => {
                if (!response.ok) {
                    callbacks.onError?.(`SSE connection failed (HTTP ${response.status})`)
                    return
                }

                const reader = response.body.getReader()
                const decoder = new TextDecoder()
                let buffer = ''

                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break

                    buffer += decoder.decode(value, { stream: true })
                    const parts = buffer.split('\n\n')
                    buffer = parts.pop() || ''  // keep incomplete chunk

                    for (const part of parts) {
                        const lines = part.split('\n')
                        let event = 'message'
                        let dataStr = ''

                        for (const line of lines) {
                            if (line.startsWith('event: ')) {
                                event = line.slice(7).trim()
                            } else if (line.startsWith('data: ')) {
                                dataStr += line.slice(6).trim() + '\n'
                            }
                        }

                        if (!dataStr.trim()) continue

                        try {
                            const data = JSON.parse(dataStr.trim())

                            if (event === 'status') {
                                callbacks.onStatus?.(data)
                            } else if (event === 'progress') {
                                callbacks.onProgress?.(data.progress ?? 0)
                            } else if (event === 'complete') {
                                callbacks.onComplete?.(data)
                                return
                            }
                        } catch {
                            // Ignore parse errors
                        }
                    }
                }
            })
            .catch((err) => {
                if (err.name !== 'AbortError') {
                    callbacks.onError?.(err.message)
                }
            })
    }

    connect()

    return () => {
        controller.abort()
    }
}

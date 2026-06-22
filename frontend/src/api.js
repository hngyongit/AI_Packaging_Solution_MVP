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
    return data  // { user_message, bot_message, conversation_id }
}

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const chatApi = {
  sendMessage: async (query: string, conversationId?: string) => {
    const response = await api.post('/chat', {
      query,
      conversation_id: conversationId,
    });
    return response.data;
  },
  getConversations: async () => {
    const response = await api.get('/conversations');
    return response.data;
  },
  getConversation: async (id: string) => {
    const response = await api.get(`/conversations/${id}`);
    return response.data;
  },
  createConversation: async () => {
    const response = await api.post('/conversations/new');
    return response.data;
  },
  updateConversation: async (id: string, data: { memory_enabled?: boolean; title?: string }) => {
    const response = await api.patch(`/conversations/${id}`, data);
    return response.data;
  },
};

export default api;

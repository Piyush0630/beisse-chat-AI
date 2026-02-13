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
};

export default api;

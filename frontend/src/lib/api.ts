import axios from 'axios';
import { useChatStore } from './store';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Response interceptor to handle connection status
api.interceptors.response.use(
  (response) => {
    useChatStore.getState().setConnected(true);
    return response;
  },
  (error) => {
    // If it's a network error or a server error, mark as disconnected
    if (!error.response || error.response.status >= 500 || error.code === 'ERR_NETWORK') {
      useChatStore.getState().setConnected(false);
    }
    return Promise.reject(error);
  }
);

export const chatApi = {
  sendMessage: async (query: string, conversationId?: string) => {
    const response = await api.post('/chat', {
      query,
      conversation_id: conversationId,
    });
    return response.data;
  },
  streamMessage: async (query: string, conversationId: string | null, onChunk: (data: any) => void) => {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to stream message');
    }

    const reader = response.body?.getReader();
    if (!reader) return;

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.trim()) {
          try {
            const data = JSON.parse(line);
            onChunk(data);
          } catch (e) {
            console.error('Error parsing stream chunk', e);
          }
        }
      }
    }
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
  uploadFile: async (conversationId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/files/upload?conversation_id=${conversationId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  getFiles: async (conversationId: string) => {
    const response = await api.get(`/files/${conversationId}`);
    return response.data;
  },
  deleteFile: async (fileId: string) => {
    const response = await api.delete(`/files/${fileId}`);
    return response.data;
  },
};

export default api;

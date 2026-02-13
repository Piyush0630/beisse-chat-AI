import { create } from 'zustand';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: { page: number; manual: string }[];
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [
    {
      id: "1",
      role: "assistant",
      content: "Hello! I am your Biesse Chat Assistant. How can I help you today?",
    }
  ],
  isLoading: false,
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  setLoading: (loading) => set({ isLoading: loading }),
  clearMessages: () => set({ messages: [] }),
}));

import { create } from 'zustand';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: { page: number; filename: string; bbox: any }[];
  actions?: { id: string; label: string; type: string }[];
}

export interface Conversation {
  id: string;
  title: string;
  updated_at: string;
  memory_enabled: boolean;
}

interface ChatState {
  messages: Message[];
  conversations: Conversation[];
  currentConversationId: string | null;
  memoryEnabled: boolean;
  isLoading: boolean;
  pdfConfig: {
    fileUrl: string | null;
    pageNumber: number;
    filename: string | null;
    highlights: any[];
  };
  
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversationId: (id: string | null) => void;
  setMemoryEnabled: (enabled: boolean) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
  setPdfConfig: (config: Partial<ChatState['pdfConfig']>) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  conversations: [],
  currentConversationId: null,
  memoryEnabled: true,
  isLoading: false,
  pdfConfig: {
    fileUrl: null,
    pageNumber: 1,
    filename: null,
    highlights: [],
  },
  
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  setConversations: (conversations) => set({ conversations }),
  setCurrentConversationId: (id) => set({ currentConversationId: id }),
  setMemoryEnabled: (enabled) => set({ memoryEnabled: enabled }),
  setLoading: (loading) => set({ isLoading: loading }),
  clearMessages: () => set({ messages: [] }),
  setPdfConfig: (config) => set((state) => ({
    pdfConfig: { ...state.pdfConfig, ...config }
  })),
}));

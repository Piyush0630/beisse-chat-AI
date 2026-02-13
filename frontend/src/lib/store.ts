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

export interface FileItem {
  id: string;
  filename: string;
  processed: boolean;
  file_type?: string;
}

interface ChatState {
  messages: Message[];
  conversations: Conversation[];
  currentConversationId: string | null;
  memoryEnabled: boolean;
  isLoading: boolean;
  isHistoryLoading: boolean;
  isConnected: boolean;
  attachedFiles: FileItem[];
  pdfConfig: {
    fileUrl: string | null;
    pageNumber: number;
    filename: string | null;
    highlights: any[];
  };
  
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversationId: (id: string | null) => void;
  setMemoryEnabled: (enabled: boolean) => void;
  setLoading: (loading: boolean) => void;
  setHistoryLoading: (loading: boolean) => void;
  setConnected: (connected: boolean) => void;
  clearMessages: () => void;
  setPdfConfig: (config: Partial<ChatState['pdfConfig']>) => void;
  setAttachedFiles: (files: FileItem[]) => void;
  addAttachedFile: (file: FileItem) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  conversations: [],
  currentConversationId: null,
  memoryEnabled: true,
  isLoading: false,
  isHistoryLoading: false,
  isConnected: true,
  attachedFiles: [],
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
  updateMessage: (id, updates) => set((state) => ({
    messages: state.messages.map((m) => m.id === id ? { ...m, ...updates } : m)
  })),
  setConversations: (conversations) => set({ conversations }),
  setCurrentConversationId: (id) => set({ currentConversationId: id }),
  setMemoryEnabled: (enabled) => set({ memoryEnabled: enabled }),
  setLoading: (loading) => set({ isLoading: loading }),
  setHistoryLoading: (loading) => set({ isHistoryLoading: loading }),
  setConnected: (connected) => set({ isConnected: connected }),
  clearMessages: () => set({ messages: [] }),
  setPdfConfig: (config) => set((state) => ({
    pdfConfig: { ...state.pdfConfig, ...config }
  })),
  setAttachedFiles: (files) => set({ attachedFiles: files }),
  addAttachedFile: (file) => set((state) => ({
    attachedFiles: [...state.attachedFiles, file]
  })),
}));

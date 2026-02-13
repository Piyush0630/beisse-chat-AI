"use client";

import React, { useEffect, useState } from "react";
import { useChatStore } from "@/lib/store";
import { chatApi } from "@/lib/api";
import { MessageSquare, Plus, Trash2, Search } from "lucide-react";

export default function HistorySidebar() {
  const [searchTerm, setSearchTerm] = useState("");
  const {
    conversations, 
    setConversations, 
    currentConversationId, 
    setCurrentConversationId,
    setMessages,
    setMemoryEnabled,
    setLoading,
    isHistoryLoading,
    setHistoryLoading,
    setAttachedFiles
  } = useChatStore();

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setHistoryLoading(true);
        const data = await chatApi.getConversations();
        setConversations(data);
      } catch (error) {
        console.error("Failed to fetch conversations", error);
      } finally {
        setHistoryLoading(false);
      }
    };
    fetchConversations();
  }, [setConversations, setHistoryLoading]);

  const handleNewChat = async () => {
    try {
      setLoading(true);
      const newConv = await chatApi.createConversation();
      setConversations([newConv, ...conversations]);
      setCurrentConversationId(newConv.id);
      setMessages([]);
      setMemoryEnabled(true);
      setAttachedFiles([]);
    } catch (error) {
      console.error("Failed to create new chat", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectConversation = async (id: string) => {
    if (id === currentConversationId) return;
    
    try {
      setLoading(true);
      const data = await chatApi.getConversation(id);
      setCurrentConversationId(id);
      setMessages(data.messages);
      setMemoryEnabled(data.memory_enabled);
      
      // Fetch files
      const files = await chatApi.getFiles(id);
      setAttachedFiles(files);
    } catch (error) {
      console.error("Failed to fetch conversation details", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this conversation?")) return;

    try {
      await chatApi.deleteConversation(id);
      setConversations(conversations.filter(c => c.id !== id));
      if (currentConversationId === id) {
        setCurrentConversationId(null);
        setMessages([]);
        setAttachedFiles([]);
      }
    } catch (error) {
      console.error("Failed to delete conversation", error);
    }
  };

  return (
    <aside className="w-full h-full border-r bg-zinc-50 dark:bg-zinc-900/50 flex flex-col overflow-hidden">
      <div className="p-4 border-b space-y-3">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 py-2.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          New Chat
        </button>

        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-zinc-400" />
          <input
            type="text"
            placeholder="Search chats..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-md border border-zinc-200 bg-white pl-9 pr-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-zinc-800 dark:bg-zinc-950"
          />
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        <div className="space-y-4">
          <div className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Recent Chats
          </div>
          <div className="space-y-1">
            {isHistoryLoading ? (
              // Skeletons
              Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex items-center gap-2 rounded-md px-3 py-2 animate-pulse">
                  <div className="h-4 w-4 rounded bg-zinc-200 dark:bg-zinc-800 shrink-0" />
                  <div className="h-4 w-3/4 rounded bg-zinc-200 dark:bg-zinc-800" />
                </div>
              ))
            ) : conversations.length === 0 ? (
              <p className="text-sm text-zinc-500 italic px-3">No conversations yet</p>
            ) : (
              conversations
                .filter(conv => conv.title.toLowerCase().includes(searchTerm.toLowerCase()))
                .map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv.id)}
                  className={`group flex items-center gap-2 rounded-md px-3 py-2 text-sm cursor-pointer transition-colors ${
                    currentConversationId === conv.id
                      ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400"
                      : "text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
                  }`}
                >
                  <MessageSquare className="h-4 w-4 shrink-0" />
                  <span className="truncate flex-1">{conv.title}</span>
                  <button
                    onClick={(e) => handleDeleteConversation(e, conv.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-600 transition-all"
                    title="Delete conversation"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}

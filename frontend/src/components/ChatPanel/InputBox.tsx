"use client";

import React from "react";
import { Send, Paperclip, Loader2 } from "lucide-react";
import { useChatStore } from "@/lib/store";
import { chatApi } from "@/lib/api";

export default function InputBox() {
  const [input, setInput] = React.useState("");
  const { addMessage, isLoading, setLoading } = useChatStore();

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: input.trim(),
    };

    addMessage(userMessage);
    setInput("");
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(userMessage.content);
      
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: response.answer,
        sources: response.sources?.map((s: any) => ({
          page: s.page,
          manual: s.manual_name || s.manual_file
        }))
      };

      addMessage(assistantMessage);
    } catch (error) {
      console.error("Failed to send message:", error);
      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: "Sorry, I encountered an error. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-end gap-2">
      <button className="p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg text-zinc-500">
        <Paperclip className="h-5 w-5" />
      </button>
      
      <div className="flex-1 relative">
        <textarea
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about machine operation..."
          className="w-full resize-none rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-sm"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
          disabled={isLoading}
        />
        
        <button 
          onClick={handleSendMessage}
          className="absolute right-2 bottom-2 p-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          disabled={!input.trim() || isLoading}
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </button>
      </div>
    </div>
  );
}

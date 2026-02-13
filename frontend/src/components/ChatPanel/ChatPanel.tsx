"use client";

import React from "react";
import MessageList from "@/components/ChatPanel/MessageList";
import InputBox from "@/components/ChatPanel/InputBox";
import { BrainCircuit } from "lucide-react";
import { useChatStore } from "@/lib/store";
import { chatApi } from "@/lib/api";

export default function ChatPanel() {
  const { memoryEnabled, setMemoryEnabled, currentConversationId } = useChatStore();

  const handleToggleMemory = async () => {
    const newValue = !memoryEnabled;
    setMemoryEnabled(newValue);
    
    if (currentConversationId) {
      try {
        await chatApi.updateConversation(currentConversationId, { memory_enabled: newValue });
      } catch (error) {
        console.error("Failed to update memory setting on backend", error);
      }
    }
  };

  return (
    <section className="flex h-full flex-col bg-white dark:bg-zinc-950 border-r">
      <div className="flex h-12 items-center justify-between border-b px-4">
        <div className="flex items-center gap-2">
          <BrainCircuit className={`h-5 w-5 ${memoryEnabled ? 'text-blue-500' : 'text-zinc-400'}`} />
          <span className="text-sm font-medium">Memory Mode</span>
        </div>
        
        <button 
          onClick={handleToggleMemory}
          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${memoryEnabled ? 'bg-blue-600' : 'bg-zinc-300'}`}
        >
          <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${memoryEnabled ? 'translate-x-5' : 'translate-x-0.5'}`} />
        </button>
      </div>
      
      <div className="flex-1 overflow-hidden">
        <MessageList />
      </div>
      
      <div className="p-4 border-t">
        <InputBox />
      </div>
    </section>
  );
}

"use client";

import React from "react";
import MessageList from "@/components/ChatPanel/MessageList";
import InputBox from "@/components/ChatPanel/InputBox";
import { useChatStore } from "@/lib/store";
import { chatApi } from "@/lib/api";

export default function ChatPanel() {
  const { memoryEnabled, setMemoryEnabled, currentConversationId } = useChatStore();

  return (
    <section className="flex h-full flex-col bg-zinc-950 border-r border-zinc-800 text-zinc-100">
      
      <div className="flex-1 overflow-hidden">
        <MessageList />
      </div>
      
      <div className="p-4 border-t border-zinc-800">
        <InputBox />
      </div>
    </section>
  );
}

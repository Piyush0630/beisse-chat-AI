"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { User, Bot, FileText } from "lucide-react";
import { useChatStore } from "@/lib/store";
import ActionButtons from "./ActionButtons";
import { API_BASE_URL } from "@/lib/api";

export default function MessageList() {
  const messages = useChatStore((state) => state.messages);
  const setPdfConfig = useChatStore((state) => state.setPdfConfig);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div ref={scrollRef} className="flex h-full flex-col overflow-y-auto p-4 space-y-6">
      {messages.map((msg) => (
        <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          {msg.role === 'assistant' && (
            <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 flex-shrink-0">
              <Bot className="h-5 w-5" />
            </div>
          )}
          
          <div className={`max-w-[85%] rounded-2xl px-4 py-2 ${
            msg.role === 'user' 
              ? 'bg-blue-600 text-white' 
              : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100'
          }`}>
            <div className="prose dark:prose-invert prose-sm max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.content}
              </ReactMarkdown>
            </div>
            
            {msg.sources && msg.sources.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2 border-t pt-2 border-zinc-200 dark:border-zinc-700">
                {msg.sources.map((src, i) => (
                  <button
                    key={i}
                    onClick={() => setPdfConfig({
                      filename: src.filename,
                      pageNumber: src.page,
                      highlights: src.bbox ? [src.bbox] : [],
                      fileUrl: `${API_BASE_URL}/files/${src.filename}`
                    })}
                    className="flex items-center gap-1.5 text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    <FileText className="h-3 w-3" />
                    Page {src.page}
                  </button>
                ))}
              </div>
            )}

            {msg.actions && msg.actions.length > 0 && (
              <ActionButtons actions={msg.actions} />
            )}
          </div>

          {msg.role === 'user' && (
            <div className="h-8 w-8 rounded-full bg-zinc-200 flex items-center justify-center text-zinc-600 flex-shrink-0">
              <User className="h-5 w-5" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

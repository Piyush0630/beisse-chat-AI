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
              : 'bg-zinc-800 text-zinc-100'
          }`}>
            <div className="prose dark:prose-invert prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  a: ({ href, children }) => {
                    if (href?.startsWith('#source-')) {
                      const idx = parseInt(href.replace('#source-', ''));
                      const src = msg.sources?.[idx];
                      if (!src) return null;
                      
                      return (
                        <span
                          className="text-blue-500 hover:underline cursor-pointer text-sm ml-2 inline-flex items-center"
                          onClick={() => {
                            const filename = src.rel_path || src.filename;
                            const fileUrl = `${API_BASE_URL}/pdf-viewer/${encodeURIComponent(filename)}`;
                            setPdfConfig({
                              filename: src.filename,
                              pageNumber: src.page,
                              highlights: src.bbox ? [src.bbox] : [],
                              fileUrl: fileUrl
                            });
                          }}
                        >
                          [View Context]
                        </span>
                      );
                    }
                    return <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>;
                  }
                }}
              >
                {(() => {
                  if (!msg.sources || msg.sources.length === 0 || msg.role === 'user') return msg.content;
                  
                  const blocks = msg.content.split(/\n\n/);
                  let sourceIdx = 0;
                  const processedBlocks = blocks.map(block => {
                    if (block.trim().startsWith('* ') || block.trim().startsWith('- ') || /^\d+\. /.test(block.trim())) {
                      const items = block.split('\n');
                      return items.map(item => {
                        if (item.trim() && sourceIdx < msg.sources!.length) {
                          return `${item} [View Context](#source-${sourceIdx++})`;
                        }
                        return item;
                      }).join('\n');
                    } else {
                      if (block.trim() && sourceIdx < msg.sources!.length) {
                        return `${block} [View Context](#source-${sourceIdx++})`;
                      }
                      return block;
                    }
                  });

                  // If there are still sources left, append them to the last block
                  if (sourceIdx < msg.sources.length) {
                    let remaining = "";
                    while (sourceIdx < msg.sources.length) {
                      remaining += ` [View Context](#source-${sourceIdx++})`;
                    }
                    processedBlocks[processedBlocks.length - 1] += remaining;
                  }
                  
                  return processedBlocks.join('\n\n');
                })()}
              </ReactMarkdown>
            </div>

            {msg.actions && msg.actions.length > 0 && (
              <ActionButtons actions={msg.actions} sources={msg.sources} />
            )}
          </div>

          {msg.role === 'user' && (
            <div className="h-8 w-8 rounded-full bg-zinc-800 flex items-center justify-center text-zinc-400 flex-shrink-0">
              <User className="h-5 w-5" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

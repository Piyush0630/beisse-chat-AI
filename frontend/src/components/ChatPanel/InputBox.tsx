"use client";

import React from "react";
import { Send, Paperclip, Loader2 } from "lucide-react";
import { useChatStore } from "@/lib/store";
import { chatApi } from "@/lib/api";

export default function InputBox() {
  const [input, setInput] = React.useState("");
  const [isUploading, setIsUploading] = React.useState(false);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const {
    addMessage,
    updateMessage,
    isLoading,
    setLoading,
    currentConversationId,
    setCurrentConversationId,
    setConversations,
    addAttachedFile
  } = useChatStore();

  // Focus textarea on mount and after loading ends
  React.useEffect(() => {
    if (!isLoading) {
      textareaRef.current?.focus();
    }
  }, [isLoading]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: input.trim(),
    };

    addMessage(userMessage);
    const query = input.trim();
    setInput("");
    setLoading(true);

    const assistantMsgId = (Date.now() + 1).toString();
    // Pre-add empty assistant message
    addMessage({
      id: assistantMsgId,
      role: 'assistant' as const,
      content: "",
    });

    let fullContent = "";

    try {
      await chatApi.streamMessage(query, currentConversationId, async (data) => {
        if (data.type === 'metadata') {
          // If it was a new conversation, update the current id and refresh the sidebar
          if (!currentConversationId && data.conversation_id) {
            setCurrentConversationId(data.conversation_id);
            const convs = await chatApi.getConversations();
            setConversations(convs);
          }
          
          if (data.sources) {
            updateMessage(assistantMsgId, {
              sources: data.sources.map((s: any) => ({
                page: s.page,
                filename: s.filename,
                bbox: s.bbox
              }))
            });
          }
        } else if (data.type === 'content') {
          fullContent += data.content;
          updateMessage(assistantMsgId, { content: fullContent });
        } else if (data.type === 'final') {
          if (data.actions) {
            updateMessage(assistantMsgId, { actions: data.actions });
          }
          if (data.message_id) {
            updateMessage(assistantMsgId, { id: data.message_id });
          }
        }
      });
    } catch (error) {
      console.error("Failed to send message:", error);
      updateMessage(assistantMsgId, {
        content: "Sorry, I encountered an error. Please try again.",
      });
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    let conversationId = currentConversationId;
    
    setIsUploading(true);
    try {
      // If no conversation exists, create one first
      if (!conversationId) {
        const newConv = await chatApi.createConversation();
        conversationId = newConv.id;
        setCurrentConversationId(conversationId);
        const convs = await chatApi.getConversations();
        setConversations(convs);
      }

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const response = await chatApi.uploadFile(conversationId!, file);
        addAttachedFile({
          id: response.file_id,
          filename: response.filename,
          processed: response.chunks_ingested > 0,
          file_type: response.filename.split('.').pop()
        });
      }
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to upload file. Please try again.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-end gap-2">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          multiple
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading || isLoading}
          className="p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg text-zinc-500 disabled:opacity-50"
          title="Upload files"
        >
          {isUploading ? (
            <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
          ) : (
            <Paperclip className="h-5 w-5" />
          )}
        </button>
        
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
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
    </div>
  );
}

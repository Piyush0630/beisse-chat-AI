"use client";

import React from "react";
import { Send, Paperclip, Loader2, FileText, X } from "lucide-react";
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
    addAttachedFile,
    attachedFiles,
    setAttachedFiles
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
                rel_path: s.rel_path,
                chunk_id: s.chunk_id,
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
          id: Math.random().toString(36).substr(2, 9),
          filename: response.filename,
          processed: true,
          file_type: response.filename.split('.').pop()
        });
      }
      alert("Files added to session context.");
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to upload file. Please try again.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const removeFile = (id: string) => {
    setAttachedFiles(attachedFiles.filter(f => f.id !== id));
  };

  return (
    <div className="flex flex-col gap-2">
      {/* Attached Files List */}
      {attachedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-1 px-1">
          {attachedFiles.map((file) => (
            <div 
              key={file.id} 
              className="flex items-center gap-1.5 bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded text-[10px] text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700"
            >
              <FileText className="h-3 w-3" />
              <span className="max-w-[100px] truncate">{file.filename}</span>
              <button onClick={() => removeFile(file.id)} className="hover:text-red-500">
                <X className="h-2.5 w-2.5" />
              </button>
            </div>
          ))}
        </div>
      )}

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
          title="Upload session files"
        >
          {isUploading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Paperclip className="h-5 w-5" />
          )}
        </button>

        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="Ask about machine operation..."
            className="w-full resize-none bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl py-2.5 pl-4 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            style={{ maxHeight: '200px' }}
          />
          <button
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
            className="absolute right-2 bottom-1.5 p-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:bg-zinc-400 transition-colors"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

"use client";

import React from "react";
import { X, FileText, UploadCloud, Loader2 } from "lucide-react";
import { useChatStore } from "@/lib/store";
import { chatApi } from "@/lib/api";

export default function FileUpload() {
  const { currentConversationId, attachedFiles, setAttachedFiles, addAttachedFile } = useChatStore();
  const [isUploading, setIsUploading] = React.useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0 || !currentConversationId) return;

    setIsUploading(true);
    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const response = await chatApi.uploadFile(currentConversationId, file);
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

  const removeFile = async (fileId: string) => {
    try {
      await chatApi.deleteFile(fileId);
      setAttachedFiles(attachedFiles.filter(f => f.id !== fileId));
    } catch (error) {
      console.error("Delete failed:", error);
    }
  };

  if (!currentConversationId) return null;

  return (
    <div className="px-4 py-2 border-t border-zinc-100 dark:border-zinc-800">
      <div className="flex flex-wrap gap-2 mb-2">
        {attachedFiles.map((file) => (
          <div 
            key={file.id} 
            className="flex items-center gap-2 bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded-md text-xs group"
          >
            <FileText className="h-3 w-3 text-zinc-500" />
            <span className="max-w-[120px] truncate">{file.filename}</span>
            <button 
              onClick={() => removeFile(file.id)}
              className="hover:text-red-500 text-zinc-400"
            >
              <X className="h-3 w-3" />
            </button>
          </div>
        ))}
        {isUploading && (
          <div className="flex items-center gap-2 bg-zinc-50 dark:bg-zinc-900 px-2 py-1 rounded-md text-xs border border-zinc-200 dark:border-zinc-800">
            <Loader2 className="h-3 w-3 animate-spin text-blue-500" />
            <span>Uploading...</span>
          </div>
        )}
      </div>

      <input 
        type="file" 
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden" 
        multiple
      />
      
      <button 
        onClick={() => fileInputRef.current?.click()}
        disabled={isUploading}
        className="flex items-center gap-2 text-xs text-blue-600 hover:text-blue-700 font-medium"
      >
        <UploadCloud className="h-3 w-3" />
        Add context files (PDF, TXT, CSV)
      </button>
    </div>
  );
}

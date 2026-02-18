"use client";

import React, { useEffect, useState, useRef } from "react";
import { Upload, RefreshCw, Trash2, FileText, ChevronDown } from "lucide-react";
import { pdfApi } from "@/lib/api";

interface PDFFile {
  id: string;
  filename: string;
  processed: boolean;
}

export default function TopToolbar() {
  const [pdfs, setPdfs] = useState<PDFFile[]>([]);
  const [selectedPdfId, setSelectedPdfId] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const replaceInputRef = useRef<HTMLInputElement>(null);

  const fetchPdfs = async () => {
    try {
      const data = await pdfApi.listPdfs();
      setPdfs(data);
      if (data.length > 0 && !selectedPdfId) {
        setSelectedPdfId(data[0].id);
      }
    } catch (error) {
      console.error("Failed to fetch PDFs", error);
    }
  };

  useEffect(() => {
    fetchPdfs();
  }, []);

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    try {
      const newPdf = await pdfApi.uploadPdf(file);
      await fetchPdfs();
      if (newPdf && newPdf.id) {
        setSelectedPdfId(newPdf.id);
      }
      if (fileInputRef.current) fileInputRef.current.value = "";
      alert("Document uploaded and indexed globally.");
    } catch (error) {
      console.error("Upload failed", error);
      alert("Upload failed. Please ensure the file is a PDF.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReplace = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !selectedPdfId) return;

    setIsLoading(true);
    try {
      await pdfApi.replacePdf(selectedPdfId, file);
      await fetchPdfs();
      if (replaceInputRef.current) replaceInputRef.current.value = "";
    } catch (error) {
      console.error("Replace failed", error);
      alert("Replace failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedPdfId) return;
    if (!confirm("Are you sure you want to delete this PDF?")) return;

    setIsLoading(true);
    try {
      await pdfApi.deletePdf(selectedPdfId);
      const updatedPdfs = pdfs.filter(p => p.id !== selectedPdfId);
      setPdfs(updatedPdfs);
      setSelectedPdfId(updatedPdfs.length > 0 ? updatedPdfs[0].id : "");
    } catch (error) {
      console.error("Delete failed", error);
      alert("Delete failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReembed = async () => {
    if (!selectedPdfId) return;

    setIsLoading(true);
    try {
      await pdfApi.reembedPdf(selectedPdfId);
      await fetchPdfs();
      alert("Re-embedding successful");
    } catch (error) {
      console.error("Re-embed failed", error);
      alert("Re-embed failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center gap-2 p-2 bg-zinc-50 dark:bg-zinc-900 border-b overflow-x-auto no-scrollbar">
      <div className="flex items-center gap-2 mr-4">
        <input
          type="file"
          accept=".pdf"
          className="hidden"
          ref={fileInputRef}
          onChange={handleUpload}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium transition-colors disabled:opacity-50"
        >
          <Upload className="h-4 w-4" />
          Upload PDF
        </button>
      </div>

      {pdfs.length > 0 && (
        <>
          <div className="h-6 w-px bg-zinc-300 dark:bg-zinc-700 mx-2" />
          
          <div className="flex items-center gap-2">
            <div className="relative">
              <select
                value={selectedPdfId}
                onChange={(e) => setSelectedPdfId(e.target.value)}
                className="appearance-none pl-8 pr-10 py-1.5 bg-white dark:bg-zinc-800 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[200px]"
              >
                {pdfs.map((pdf) => (
                  <option key={pdf.id} value={pdf.id}>
                    {pdf.filename} {pdf.processed ? "" : "(Not processed)"}
                  </option>
                ))}
              </select>
              <FileText className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
              <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500 pointer-events-none" />
            </div>

            <input
              type="file"
              accept=".pdf"
              className="hidden"
              ref={replaceInputRef}
              onChange={handleReplace}
            />
            <button
              onClick={() => replaceInputRef.current?.click()}
              disabled={isLoading || !selectedPdfId}
              className="flex items-center gap-1.5 px-3 py-1.5 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded text-sm font-medium transition-colors disabled:opacity-50"
              title="Replace PDF"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Replace
            </button>

            <button
              onClick={handleReembed}
              disabled={isLoading || !selectedPdfId}
              className="flex items-center gap-1.5 px-3 py-1.5 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded text-sm font-medium transition-colors disabled:opacity-50"
              title="Re-embed PDF"
            >
              <RefreshCw className="h-4 w-4" />
              Re-embed
            </button>

            <button
              onClick={handleDelete}
              disabled={isLoading || !selectedPdfId}
              className="flex items-center gap-1.5 px-3 py-1.5 hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 rounded text-sm font-medium transition-colors disabled:opacity-50"
              title="Delete PDF"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </button>
          </div>
        </>
      )}
      
      {isLoading && (
        <div className="ml-auto pr-4 text-xs text-zinc-500 flex items-center gap-2">
          <div className="h-2 w-2 bg-blue-600 rounded-full animate-pulse" />
          Processing...
        </div>
      )}
    </div>
  );
}

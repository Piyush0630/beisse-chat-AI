"use client";

import React from "react";
import { Maximize2, Minimize2, Search, ZoomIn, ZoomOut, ChevronLeft, ChevronRight } from "lucide-react";
import { Document, Page, pdfjs } from "react-pdf";
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set up the worker for react-pdf
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

import { useChatStore } from "@/lib/store";

export default function PDFViewerPanel() {
  const pdfConfig = useChatStore((state) => state.pdfConfig);
  const setPdfConfig = useChatStore((state) => state.setPdfConfig);
  
  const [numPages, setNumPages] = React.useState<number>(0);
  const [scale, setScale] = React.useState<number>(1.0);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
  }

  const setPageNumber = (p: number | ((prev: number) => number)) => {
    const newPage = typeof p === 'function' ? p(pdfConfig.pageNumber) : p;
    setPdfConfig({ pageNumber: newPage });
  };

  const pageNumber = pdfConfig.pageNumber;

  return (
    <section className="flex h-full flex-col bg-zinc-100 dark:bg-zinc-900">
      <div className="flex h-12 items-center justify-between border-b bg-white px-4 dark:bg-zinc-950">
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium truncate max-w-[200px]">
            {pdfConfig.filename || "No document selected"}
          </span>
          <div className="flex items-center gap-2 bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded">
            <button 
              onClick={() => setPageNumber(p => Math.max(1, p - 1))}
              className="p-0.5 hover:bg-zinc-200 dark:hover:bg-zinc-700 rounded disabled:opacity-30"
              disabled={pageNumber <= 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="text-xs min-w-[60px] text-center">
              Page {pageNumber} / {numPages || '--'}
            </span>
            <button 
              onClick={() => setPageNumber(p => Math.min(numPages, p + 1))}
              className="p-0.5 hover:bg-zinc-200 dark:hover:bg-zinc-700 rounded disabled:opacity-30"
              disabled={pageNumber >= numPages}
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setScale(s => Math.max(0.5, s - 0.1))}
            className="p-1.5 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <span className="text-xs w-10 text-center">{Math.round(scale * 100)}%</span>
          <button 
            onClick={() => setScale(s => Math.min(2.0, s + 0.1))}
            className="p-1.5 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <div className="h-4 w-px bg-zinc-200 dark:bg-zinc-800 mx-1" />
          <button className="p-1.5 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded">
            <Search className="h-4 w-4" />
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto p-8 flex justify-center bg-zinc-200 dark:bg-zinc-900">
        <div className="shadow-2xl">
          <Document
            file={pdfConfig.fileUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            loading={
              <div className="h-[842px] w-[595px] bg-white dark:bg-zinc-800 flex items-center justify-center text-zinc-400">
                Loading PDF...
              </div>
            }
            noData={
              <div className="h-[842px] w-[595px] bg-white dark:bg-zinc-800 flex items-center justify-center text-zinc-400">
                Select a citation to load PDF
              </div>
            }
          >
            {numPages > 0 && (
              <div className="relative">
                <Page
                  pageNumber={pageNumber}
                  scale={scale}
                  renderAnnotationLayer={true}
                  renderTextLayer={true}
                />
                {pdfConfig.highlights.map((bbox, idx) => (
                  <div
                    key={idx}
                    className="absolute border-2 border-orange-400 bg-yellow-400/30 pointer-events-none z-10"
                    style={{
                      left: bbox.x * scale,
                      top: bbox.y * scale,
                      width: bbox.width * scale,
                      height: bbox.height * scale,
                    }}
                  />
                ))}
              </div>
            )}
          </Document>
        </div>
      </div>
    </section>
  );
}

"use client";

import React from "react";
import { Maximize2, Minimize2, Search, ZoomIn, ZoomOut, ChevronLeft, ChevronRight, X } from "lucide-react";
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
  const [showSearch, setShowSearch] = React.useState(false);
  const [pdfSearchTerm, setPdfSearchTerm] = React.useState("");
  const [containerWidth, setContainerWidth] = React.useState<number>(0);
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (containerRef.current) {
      const resizeObserver = new ResizeObserver((entries) => {
        for (let entry of entries) {
          setContainerWidth(entry.contentRect.width);
        }
      });
      resizeObserver.observe(containerRef.current);
      return () => resizeObserver.disconnect();
    }
  }, []);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
  }

  const setPageNumber = (p: number | ((prev: number) => number)) => {
    const newPage = typeof p === 'function' ? p(pdfConfig.pageNumber) : p;
    setPdfConfig({ pageNumber: newPage });
  };

  const pageNumber = pdfConfig.pageNumber;

  return (
    <section className="flex h-full flex-col bg-zinc-100 dark:bg-zinc-900 min-w-0">
      <div className="flex h-12 items-center justify-between border-b bg-white px-2 dark:bg-zinc-950 gap-2 min-w-0">
        <div className="flex items-center gap-2 min-w-0 overflow-hidden">
          <span className="text-sm font-medium truncate shrink hidden sm:inline">
            {pdfConfig.filename || "No document"}
          </span>
          <div className="flex items-center gap-1 bg-zinc-100 dark:bg-zinc-800 px-1.5 py-1 rounded shrink-0">
            <button
              onClick={() => setPageNumber(p => Math.max(1, p - 1))}
              className="p-0.5 hover:bg-zinc-200 dark:hover:bg-zinc-700 rounded disabled:opacity-30"
              disabled={pageNumber <= 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="text-[10px] sm:text-xs min-w-[50px] text-center">
              {pageNumber} / {numPages || '--'}
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
        
        <div className="flex items-center gap-1 shrink-0">
          <div className="hidden xs:flex items-center gap-1">
            <button
              onClick={() => setScale(s => Math.max(0.5, s - 0.1))}
              className="p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded"
            >
              <ZoomOut className="h-3.5 w-3.5" />
            </button>
            <span className="text-[10px] w-8 text-center">{Math.round(scale * 100)}%</span>
            <button
              onClick={() => setScale(s => Math.min(2.0, s + 0.1))}
              className="p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded"
            >
              <ZoomIn className="h-3.5 w-3.5" />
            </button>
          </div>
          
          <div className="h-4 w-px bg-zinc-200 dark:bg-zinc-800 mx-0.5" />
          
          <div className="flex items-center">
            {showSearch && containerWidth > 400 && (
              <input
                autoFocus
                type="text"
                placeholder="Find..."
                value={pdfSearchTerm}
                onChange={(e) => setPdfSearchTerm(e.target.value)}
                className="w-20 sm:w-28 rounded-md border border-zinc-200 bg-white px-1.5 py-0.5 text-[10px] focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-zinc-800 dark:bg-zinc-950 mr-1"
              />
            )}
            <button
              onClick={() => setShowSearch(!showSearch)}
              className={`p-1.5 rounded transition-colors ${showSearch ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/40' : 'hover:bg-zinc-100 dark:hover:bg-zinc-800'}`}
              title="Search in PDF"
            >
              <Search className="h-4 w-4" />
            </button>
          </div>
          <button
            onClick={() => setPdfConfig({ fileUrl: null, filename: null, highlights: [] })}
            className="p-1.5 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 rounded"
            title="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
      
      <div
        ref={containerRef}
        className="flex-1 overflow-auto bg-zinc-200 dark:bg-zinc-900"
      >
        <div className="min-h-full p-8 flex justify-center items-start">
          <div className="shadow-2xl bg-white dark:bg-zinc-800">
            <Document
              file={pdfConfig.fileUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              loading={
                <div
                  style={{ width: containerWidth > 100 ? containerWidth - 64 : 595 }}
                  className="h-[842px] flex items-center justify-center text-zinc-400"
                >
                  Loading PDF...
                </div>
              }
              noData={
                <div
                  style={{ width: containerWidth > 100 ? containerWidth - 64 : 595 }}
                  className="h-[842px] flex items-center justify-center text-zinc-400"
                >
                  Select a citation to load PDF
                </div>
              }
            >
              {numPages > 0 && (
                <div className="relative">
                  <Page
                    pageNumber={pageNumber}
                    width={containerWidth > 100 ? containerWidth - 100 : undefined}
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
    </div>
  </section>
  );
}

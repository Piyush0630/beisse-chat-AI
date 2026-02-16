"use client";

import React from "react";
import { Maximize2, Minimize2, Search, ZoomIn, ZoomOut, ChevronLeft, ChevronRight, X } from "lucide-react";
import { Document, Page, pdfjs } from "react-pdf";
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set up the worker for react-pdf
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

import { useChatStore } from "@/lib/store";

export default function PDFViewerPanel() {
  const pdfConfig = useChatStore((state) => state.pdfConfig);
  const setPdfConfig = useChatStore((state) => state.setPdfConfig);
  
  const [numPages, setNumPages] = React.useState<number>(0);
  const [scale, setScale] = React.useState<number>(1.0);
  const [pageDimensions, setPageDimensions] = React.useState<{width: number, height: number} | null>(null);
  const [showSearch, setShowSearch] = React.useState(false);
  const [pdfSearchTerm, setPdfSearchTerm] = React.useState("");
  const [containerWidth, setContainerWidth] = React.useState<number>(0);
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (containerRef.current) {
      const resizeObserver = new ResizeObserver((entries) => {
        for (let entry of entries) {
          const newWidth = Math.floor(entry.contentRect.width);
          setContainerWidth((prev) => {
            // Keep threshold low for smooth dynamic resizing
            if (Math.abs(prev - newWidth) > 1) {
              return newWidth;
            }
            return prev;
          });
        }
      });
      resizeObserver.observe(containerRef.current);
      return () => resizeObserver.disconnect();
    }
  }, []);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
  }

  function onPageLoadSuccess(page: any) {
    setPageDimensions({ width: page.width, height: page.height });
  }

  const setPageNumber = (p: number | ((prev: number) => number)) => {
    const newPage = typeof p === 'function' ? p(pdfConfig.pageNumber) : p;
    setPdfConfig({ pageNumber: newPage, highlights: [] });
  };

  const pageNumber = pdfConfig.pageNumber;

  // Consistent width calculation for the PDF.js renderer
  const pdfRenderWidth = containerWidth > 40 ? containerWidth - 40 : 595;

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
        className="flex-1 overflow-y-scroll bg-zinc-200 dark:bg-zinc-900"
      >
        <div className="min-h-full p-4 sm:p-8 flex justify-center items-start">
          <div className="shadow-2xl bg-white dark:bg-zinc-800">
            <Document
              file={pdfConfig.fileUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={(error) => console.error("PDF Load Error:", error)}
              loading={
                <div
                  style={{ width: pdfRenderWidth }}
                  className="h-[842px] flex items-center justify-center text-zinc-400"
                >
                  Loading PDF...
                </div>
              }
              error={
                <div
                  style={{ width: pdfRenderWidth }}
                  className="h-[842px] flex flex-col items-center justify-center text-red-500 gap-2"
                >
                  <p>Failed to load PDF file.</p>
                  <p className="text-xs text-zinc-500">{pdfConfig.fileUrl}</p>
                </div>
              }
              noData={
                <div
                  style={{ width: pdfRenderWidth }}
                  className="h-[842px] flex items-center justify-center text-zinc-400"
                >
                  Select a citation to load PDF
                </div>
              }
            >
              {numPages > 0 && (
                /* Viewport Scaling Layer with CSS Aspect Ratio for instant resizing */
                <div 
                  className="relative mx-auto shadow-lg bg-white overflow-hidden"
                  style={{ 
                    width: pdfRenderWidth * scale,
                    maxWidth: '100%',
                    aspectRatio: pageDimensions ? `${pageDimensions.width} / ${pageDimensions.height}` : 'auto'
                  }}
                >
                  <Page
                    pageNumber={pageNumber}
                    onLoadSuccess={onPageLoadSuccess}
                    width={pdfRenderWidth}
                    scale={scale}
                    renderAnnotationLayer={true}
                    renderTextLayer={true}
                  />
                   {/* Highlight Rendering Layer: Uses normalized % coordinates for fluid responsiveness */}
                   {pageDimensions && pdfConfig.highlights.map((bbox, idx) => {
                     const x_norm = bbox.x_norm !== undefined ? bbox.x_norm : (bbox.x / (bbox.page_width || pageDimensions.width));
                     const y_norm = bbox.y_norm !== undefined ? bbox.y_norm : (bbox.y / (bbox.page_height || pageDimensions.height));
                     const w_norm = bbox.w_norm !== undefined ? bbox.w_norm : (bbox.width / (bbox.page_width || pageDimensions.width));
                     const h_norm = bbox.h_norm !== undefined ? bbox.h_norm : (bbox.height / (bbox.page_height || pageDimensions.height));

                     return (
                       <div
                         key={idx}
                         className="absolute border-2 border-orange-400 bg-yellow-400/30 pointer-events-none z-10"
                         style={{
                           left: `${x_norm * 100}%`,
                           top: `${y_norm * 100}%`,
                           width: `${w_norm * 100}%`,
                           height: `${h_norm * 100}%`,
                         }}
                       />
                     );
                   })}
                </div>
              )}
            </Document>
          </div>
        </div>
      </div>
    </section>
  );
}

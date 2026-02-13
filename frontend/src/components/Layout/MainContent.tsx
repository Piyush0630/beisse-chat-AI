"use client";

import React, { useState, useCallback, useRef } from "react";
import dynamic from "next/dynamic";
import HistorySidebar from "./HistorySidebar";
import ChatPanel from "../ChatPanel/ChatPanel";

const PDFViewerPanel = dynamic(() => import("./PDFViewerPanel"), { ssr: false });

export default function MainContent() {
  const [sidebarWidth, setSidebarWidth] = useState(20); // percentage
  const [pdfWidth, setPdfWidth] = useState(30); // percentage
  const isResizingSidebar = useRef(false);
  const isResizingPdf = useRef(false);

  const startResizingSidebar = useCallback(() => {
    isResizingSidebar.current = true;
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", stopResizing);
    document.body.style.cursor = "col-resize";
  }, []);

  const startResizingPdf = useCallback(() => {
    isResizingPdf.current = true;
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", stopResizing);
    document.body.style.cursor = "col-resize";
  }, []);

  const stopResizing = useCallback(() => {
    isResizingSidebar.current = false;
    isResizingPdf.current = false;
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", stopResizing);
    document.body.style.cursor = "default";
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isResizingSidebar.current) {
      const newWidth = (e.clientX / window.innerWidth) * 100;
      if (newWidth > 10 && newWidth < 30) {
        setSidebarWidth(newWidth);
      }
    } else if (isResizingPdf.current) {
      const newWidth = ((window.innerWidth - e.clientX) / window.innerWidth) * 100;
      if (newWidth > 15 && newWidth < 50) {
        setPdfWidth(newWidth);
      }
    }
  }, []);

  return (
    <div className="flex flex-1 overflow-hidden select-none">
      {/* Sidebar */}
      <div style={{ width: `${sidebarWidth}%` }} className="min-w-[200px] max-w-[400px]">
        <HistorySidebar />
      </div>
      
      {/* Divider */}
      <div 
        onMouseDown={startResizingSidebar}
        className="w-1 bg-zinc-200 dark:bg-zinc-800 hover:bg-blue-500 cursor-col-resize transition-colors"
      />

      {/* Chat */}
      <div className="flex-1 min-w-[400px]">
        <ChatPanel />
      </div>
      
      {/* Divider */}
      <div 
        onMouseDown={startResizingPdf}
        className="w-1 bg-zinc-200 dark:bg-zinc-800 hover:bg-blue-500 cursor-col-resize transition-colors"
      />

      {/* PDF Viewer */}
      <div style={{ width: `${pdfWidth}%` }} className="min-w-[250px]">
        <PDFViewerPanel />
      </div>
    </div>
  );
}

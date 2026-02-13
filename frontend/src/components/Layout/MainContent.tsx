"use client";

import React from "react";
import HistorySidebar from "./HistorySidebar";
import ChatPanel from "../ChatPanel/ChatPanel";
import PDFViewerPanel from "./PDFViewerPanel";

export default function MainContent() {
  return (
    <div className="flex flex-1 overflow-hidden">
      {/* 20% Sidebar */}
      <div className="w-1/5 min-w-[250px] max-w-[350px]">
        <HistorySidebar />
      </div>
      
      {/* 30% Chat */}
      <div className="w-[30%] min-w-[350px]">
        <ChatPanel />
      </div>
      
      {/* 50% PDF Viewer */}
      <div className="flex-1">
        <PDFViewerPanel />
      </div>
    </div>
  );
}

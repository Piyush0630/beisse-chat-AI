"use client";

import React from "react";
import dynamic from "next/dynamic";
import HistorySidebar from "./HistorySidebar";
import ChatPanel from "../ChatPanel/ChatPanel";

const PDFViewerPanel = dynamic(() => import("./PDFViewerPanel"), { ssr: false });

export default function MainContent() {
  return (
    <div className="flex flex-1 overflow-hidden">
      {/* 20% Sidebar */}
      <div className="w-1/5 min-w-[250px] max-w-[350px]">
        <HistorySidebar />
      </div>
      
      {/* 50% Chat */}
      <div className="w-1/2 min-w-[450px]">
        <ChatPanel />
      </div>
      
      {/* 30% PDF Viewer */}
      <div className="w-[30%] min-w-[300px]">
        <PDFViewerPanel />
      </div>
    </div>
  );
}

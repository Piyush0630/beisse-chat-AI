'use client'

import React from 'react'
import { ChatPanel } from '../ChatPanel/ChatPanel'
import { PDFViewerPanel } from '../PDFViewer/PDFViewerPanel'

export function MainContent() {
  return (
    <div className="flex h-full overflow-hidden">
      {/* Chat Panel - 40% */}
      <div className="w-5/12 min-w-[400px] border-r border-gray-200">
        <ChatPanel />
      </div>
      
      {/* PDF Viewer Panel - 60% */}
      <div className="flex-1">
        <PDFViewerPanel />
      </div>
    </div>
  )
}

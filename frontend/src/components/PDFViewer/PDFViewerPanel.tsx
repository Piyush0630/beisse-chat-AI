'use client'

import React, { useEffect, useState } from 'react'
import { useAppStore } from '@/lib/store'
import { HighlightOverlay } from './HighlightOverlay'

export function PDFViewerPanel() {
  const { pdf, setCurrentPage, addHighlight, selectCitation } = useAppStore()
  const [pdfDoc, setPdfDoc] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (pdf.currentFile) {
      loadPDF(pdf.currentFile)
    }
  }, [pdf.currentFile])

  const loadPDF = async (filename: string) => {
    setLoading(true)
    // TODO: Implement PDF.js loading
    // For now, show placeholder
    setLoading(false)
  }

  const handleCitationClick = (citation: any) => {
    if (citation.source?.pageNumber) {
      setCurrentPage(citation.source.pageNumber)
    }
    addHighlight(citation)
  }

  return (
    <div className="h-full bg-gray-100 flex flex-col">
      {/* PDF Toolbar */}
      <div className="bg-white border-b border-gray-200 p-2 flex gap-2 items-center">
        <button
          onClick={() => setCurrentPage(Math.max(1, pdf.currentPage - 1))}
          className="p-2 hover:bg-gray-100 rounded transition-colors"
        >
          ←
        </button>
        <span className="text-sm text-gray-600">
          Page {pdf.currentPage} {pdfDoc ? `/ ${pdfDoc.numPages || '?'}` : ''}
        </span>
        <button
          onClick={() => setCurrentPage((pdf.currentPage || 1) + 1)}
          className="p-2 hover:bg-gray-100 rounded transition-colors"
        >
          →
        </button>
        
        <div className="flex-1" />
        
        <button
          onClick={() => setCurrentPage(1)}
          className="text-sm text-gray-600 hover:text-gray-800"
        >
          First
        </button>
        <button
          onClick={() => setCurrentPage(pdfDoc?.numPages || 1)}
          className="text-sm text-gray-600 hover:text-gray-800"
        >
          Last
        </button>
      </div>
      
      {/* PDF Content */}
      <div className="flex-1 overflow-auto p-4 flex justify-center">
        <div className="relative bg-white shadow-lg">
          {loading ? (
            <div className="w-[800px] h-[1100px] flex items-center justify-center">
              <span className="text-gray-400">Loading PDF...</span>
            </div>
          ) : pdf.currentFile ? (
            <>
              {/* PDF Canvas - Placeholder */}
              <div 
                className="w-[800px] h-[1100px] flex items-center justify-center"
                style={{ minHeight: '1100px' }}
              >
                <div className="text-center text-gray-400">
                  <p className="text-lg">PDF Viewer</p>
                  <p className="text-sm">{pdf.currentFile}</p>
                  <p className="text-sm mt-2">Page {pdf.currentPage}</p>
                </div>
              </div>
              
              {/* Highlight Overlay */}
              <HighlightOverlay
                highlights={pdf.highlights.filter(
                  h => h.source?.pageNumber === pdf.currentPage
                )}
                onHighlightClick={selectCitation}
              />
            </>
          ) : (
            <div className="w-[800px] h-[1100px] flex items-center justify-center">
              <div className="text-center text-gray-400">
                <p className="text-lg mb-2">📄 No Document Loaded</p>
                <p className="text-sm">Upload a PDF to view it here</p>
                <p className="text-sm">Click on citations in chat to navigate</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

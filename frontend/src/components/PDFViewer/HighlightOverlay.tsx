'use client'

import React from 'react'

interface HighlightOverlayProps {
  highlights: any[]
  onHighlightClick: (citation: any) => void
}

export function HighlightOverlay({ highlights, onHighlightClick }: HighlightOverlayProps) {
  return (
    <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
      {highlights.map((highlight, idx) => {
        const bbox = highlight.source?.bbox
        if (!bbox) return null
        
        return (
          <div
            key={highlight.id || idx}
            className="absolute pointer-events-auto cursor-pointer"
            style={{
              left: bbox.x,
              top: bbox.y,
              width: bbox.width,
              height: bbox.height,
              backgroundColor: 'rgba(255, 200, 0, 0.3)',
              border: '2px solid rgba(255, 200, 0, 0.8)',
            }}
            onClick={() => onHighlightClick(highlight)}
            title={`${highlight.source?.manualName || 'Unknown'} - Page ${highlight.source?.pageNumber || 'N/A'}`}
          >
            <span 
              className="absolute -top-5 -left-5 bg-orange-500 text-white text-xs rounded px-1"
              style={{ fontSize: '10px' }}
            >
              {idx + 1}
            </span>
          </div>
        )
      })}
    </div>
  )
}

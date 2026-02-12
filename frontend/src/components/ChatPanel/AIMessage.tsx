'use client'

import React from 'react'

interface AIMessageProps {
  message: {
    id: string
    content: string
    citations?: any[]
    timestamp: Date
  }
  onCitationClick: (citation: any) => void
}

export function AIMessage({ message, onCitationClick }: AIMessageProps) {
  return (
    <div className="flex gap-3 p-4 bg-white rounded-lg shadow-sm">
      <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
        <span className="text-white text-sm">AI</span>
      </div>
      
      <div className="flex-1">
        <div className="prose max-w-none">
          <p className="text-gray-800 whitespace-pre-wrap">{message.content}</p>
        </div>
        
        {message.citations && message.citations.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <p className="text-xs font-semibold text-gray-500 mb-2">Sources:</p>
            <div className="space-y-2">
              {message.citations.map((citation, idx) => (
                <button
                  key={citation.id || idx}
                  onClick={() => onCitationClick(citation)}
                  className="block w-full text-left p-2 rounded bg-yellow-50 hover:bg-yellow-100 transition-colors"
                >
                  <span className="text-xs font-medium text-gray-700">
                    [{idx + 1}] {citation.source?.manualName || 'Unknown'}
                  </span>
                  <span className="text-xs text-gray-500 ml-2">
                    Page {citation.source?.pageNumber || 'N/A'}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}
        
        <p className="text-xs text-gray-400 mt-2">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  )
}

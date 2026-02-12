'use client'

import React from 'react'

interface UserMessageProps {
  message: {
    id: string
    content: string
    timestamp: Date
  }
}

export function UserMessage({ message }: UserMessageProps) {
  return (
    <div className="flex gap-3 p-4">
      <div className="w-8 h-8 rounded-full bg-gray-400 flex items-center justify-center flex-shrink-0">
        <span className="text-white text-sm">You</span>
      </div>
      
      <div className="flex-1">
        <div className="bg-gray-100 rounded-lg p-3">
          <p className="text-gray-800 whitespace-pre-wrap">{message.content}</p>
        </div>
        <p className="text-xs text-gray-400 mt-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  )
}

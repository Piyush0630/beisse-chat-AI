'use client'

import React from 'react'
import { UserMessage } from './UserMessage'
import { AIMessage } from './AIMessage'
import { useAppStore } from '@/lib/store'

interface MessageListProps {
  messages: any[]
  onCitationClick: (citation: any) => void
}

export function MessageList({ messages, onCitationClick }: MessageListProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <p className="text-lg mb-2">👋 Welcome to Biesse Chat Assistant</p>
            <p className="text-sm">Ask questions about Biesse machine documentation</p>
          </div>
        </div>
      ) : (
        messages.map((message) => (
          message.role === 'user' ? (
            <UserMessage key={message.id} message={message} />
          ) : (
            <AIMessage 
              key={message.id} 
              message={message} 
              onCitationClick={onCitationClick}
            />
          )
        ))
      )}
    </div>
  )
}

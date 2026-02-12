'use client'

import React from 'react'
import { MessageList } from './MessageList'
import { InputBox } from './InputBox'
import { useAppStore } from '@/lib/store'
import { chatApi } from '@/lib/api'

export function ChatPanel() {
  const { chat, addMessage, setLoading, selectCitation } = useAppStore()

  const handleSendMessage = async (message: string) => {
    // Add user message
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    })

    setLoading(true)

    try {
      // Call API
      const response = await chatApi.sendMessage({
        message,
        memoryEnabled: true,
      })

      // Add AI response
      addMessage({
        id: response.messageId,
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
        timestamp: new Date(),
      })
    } catch (error) {
      console.error('Chat error:', error)
      addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <MessageList 
        messages={chat.messages} 
        onCitationClick={selectCitation}
      />
      <InputBox onSend={handleSendMessage} disabled={chat.isLoading} />
    </div>
  )
}

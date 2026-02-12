'use client'

import React from 'react'
import { Header } from '@/components/Layout/Header'
import { MainContent } from '@/components/Layout/MainContent'

export default function HomePage() {
  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Header />
      <main className="flex-1 overflow-hidden">
        <MainContent />
      </main>
    </div>
  )
}

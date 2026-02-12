'use client'

import React from 'react'
import { Settings, Upload, Menu } from 'lucide-react'
import { CategorySelector } from './CategorySelector'

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold text-gray-800">
          Biesse Chat Assistant
        </h1>
        <CategorySelector />
      </div>
      
      <div className="flex items-center gap-2">
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <Upload size={20} className="text-gray-600" />
        </button>
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <Settings size={20} className="text-gray-600" />
        </button>
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors lg:hidden">
          <Menu size={20} className="text-gray-600" />
        </button>
      </div>
    </header>
  )
}

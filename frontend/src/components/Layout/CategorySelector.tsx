'use client'

import React from 'react'

const categories = [
  { id: 'all', name: 'All Categories' },
  { id: 'machine_operation', name: 'Machine Operation' },
  { id: 'maintenance', name: 'Maintenance' },
  { id: 'safety', name: 'Safety' },
  { id: 'troubleshooting', name: 'Troubleshooting' },
  { id: 'programming', name: 'Programming' },
]

export function CategorySelector() {
  return (
    <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
      {categories.map(cat => (
        <option key={cat.id} value={cat.id}>
          {cat.name}
        </option>
      ))}
    </select>
  )
}

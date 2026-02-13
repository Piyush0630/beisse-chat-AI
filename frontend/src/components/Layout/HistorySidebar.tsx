"use client";

import React from "react";

export default function HistorySidebar() {
  return (
    <aside className="w-full h-full border-r bg-zinc-50 dark:bg-zinc-900/50 p-4">
      <div className="mb-6">
        <button className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors">
          + New Chat
        </button>
      </div>
      
      <div className="space-y-4">
        <div className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Today
        </div>
        <div className="space-y-1">
          <div className="rounded-md bg-blue-50 px-3 py-2 text-sm text-blue-700 dark:bg-blue-900/20 dark:text-blue-400 cursor-pointer">
            Machine Calibration Help
          </div>
          <div className="rounded-md px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 cursor-pointer">
            Blade Replacement Steps
          </div>
        </div>
      </div>
    </aside>
  );
}

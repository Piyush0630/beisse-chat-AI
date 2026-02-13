"use client";

import React from "react";
import { X, Moon, Sun, Database, Info } from "lucide-react";
import { useChatStore } from "@/lib/store";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const { memoryEnabled, setMemoryEnabled } = useChatStore();
  const [theme, setTheme] = React.useState<'light' | 'dark'>('light');

  React.useEffect(() => {
    // Check initial theme
    if (document.documentElement.classList.contains('dark')) {
      setTheme('dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm px-4">
      <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 overflow-hidden">
        <div className="flex items-center justify-between border-b px-6 py-4 dark:border-zinc-800">
          <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
            Settings
          </h3>
          <button 
            onClick={onClose}
            className="rounded-full p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
          >
            <X className="h-5 w-5 text-zinc-500" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Appearance */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-zinc-500 uppercase tracking-wider">Appearance</h4>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {theme === 'light' ? <Sun className="h-5 w-5 text-orange-500" /> : <Moon className="h-5 w-5 text-blue-400" />}
                <span className="text-sm font-medium">Dark Mode</span>
              </div>
              <button
                onClick={toggleTheme}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                  theme === 'dark' ? 'bg-blue-600' : 'bg-zinc-200 dark:bg-zinc-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>

          {/* AI Configuration */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-zinc-500 uppercase tracking-wider">AI Configuration</h4>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Database className="h-5 w-5 text-blue-500" />
                <div>
                  <div className="text-sm font-medium">Memory Mode</div>
                  <div className="text-xs text-zinc-500">Allow AI to remember previous messages</div>
                </div>
              </div>
              <button
                onClick={() => setMemoryEnabled(!memoryEnabled)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                  memoryEnabled ? 'bg-blue-600' : 'bg-zinc-200 dark:bg-zinc-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    memoryEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>

          {/* System Info */}
          <div className="space-y-3 pt-2">
            <h4 className="text-sm font-medium text-zinc-500 uppercase tracking-wider">System Information</h4>
            <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800/50 space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-zinc-500">Model</span>
                <span className="font-medium">GPT-4o (Optimized for Biesse)</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-zinc-500">Knowledge Base</span>
                <span className="font-medium">Biesse Machine Manuals</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-zinc-500">Version</span>
                <span className="font-medium">1.2.0</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-zinc-50 px-6 py-4 dark:bg-zinc-800/50 flex justify-end">
          <button
            onClick={onClose}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200 transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

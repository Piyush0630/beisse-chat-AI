"use client";

import React from "react";
import { Settings, Wifi, WifiOff } from "lucide-react";
import { useChatStore } from "@/lib/store";
import SettingsModal from "../Modals/SettingsModal";

export default function Header() {
  const { isConnected } = useChatStore();
  const [isSettingsOpen, setIsSettingsOpen] = React.useState(false);

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6 dark:bg-zinc-950">
      <div className="flex items-center gap-4">
        <div className="h-8 w-8 rounded bg-blue-600 flex items-center justify-center text-white font-bold">
          B
        </div>
        <h1 className="text-xl font-semibold">Biesse Chat Assistant</h1>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-sm text-zinc-500">
          {isConnected ? (
            <>
              <Wifi className="h-4 w-4 text-green-500" />
              <span>Connected</span>
            </>
          ) : (
            <>
              <WifiOff className="h-4 w-4 text-red-500" />
              <span>Disconnected</span>
            </>
          )}
        </div>
        
        <button
          onClick={() => setIsSettingsOpen(true)}
          className="rounded-full p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
          title="Settings"
        >
          <Settings className="h-5 w-5" />
        </button>
      </div>

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </header>
  );
}

"use client";

import React from "react";
import { WifiOff, RefreshCcw } from "lucide-react";
import { useChatStore } from "@/lib/store";
import { chatApi } from "@/lib/api";

export default function DisconnectModal() {
  const { isConnected, setConnected } = useChatStore();
  const [isRetrying, setIsRetrying] = React.useState(false);

  const handleRetry = async () => {
    setIsRetrying(true);
    try {
      // Simple health check call
      const response = await fetch('http://localhost:8001/health');
      if (response.ok) {
        setConnected(true);
      }
    } catch (error) {
      console.error("Retry failed:", error);
    } finally {
      setIsRetrying(false);
    }
  };

  if (isConnected) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm px-4">
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
        <div className="flex flex-col items-center text-center">
          <div className="mb-4 rounded-full bg-red-100 p-3 dark:bg-red-900/30">
            <WifiOff className="h-6 w-6 text-red-600 dark:text-red-400" />
          </div>
          <h3 className="mb-2 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
            Connection Lost
          </h3>
          <p className="mb-6 text-sm text-zinc-500 dark:text-zinc-400">
            We've lost connection to the Biesse Chat server. Please check your network or try reconnecting.
          </p>
          <button
            onClick={handleRetry}
            disabled={isRetrying}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 py-2.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            <RefreshCcw className={`h-4 w-4 ${isRetrying ? 'animate-spin' : ''}`} />
            {isRetrying ? "Reconnecting..." : "Reconnect Now"}
          </button>
        </div>
      </div>
    </div>
  );
}

"use client";

import React from "react";
import { LayoutDashboard, Download, FileText, ExternalLink } from "lucide-react";

export interface Action {
  id: string;
  label: string;
  type: string;
}

interface ActionButtonsProps {
  actions: Action[];
}

export default function ActionButtons({ actions }: ActionButtonsProps) {
  if (!actions || actions.length === 0) return null;

  const getIcon = (type: string) => {
    switch (type) {
      case "navigation":
        return <LayoutDashboard className="h-3.5 w-3.5" />;
      case "file":
        return <Download className="h-3.5 w-3.5" />;
      case "pdf":
        return <FileText className="h-3.5 w-3.5" />;
      default:
        return <ExternalLink className="h-3.5 w-3.5" />;
    }
  };

  const handleActionClick = (action: Action) => {
    console.log(`Action clicked: ${action.id}`, action);
    // For now, we just log. In a real app, this would trigger navigation or specific logic.
    if (action.id === "view_dashboard") {
       alert("Navigating to Dashboard (Simulation)");
    } else if (action.id === "download_report") {
       alert("Downloading Report (Simulation)");
    } else if (action.id === "open_manual") {
       alert("Opening Manual (Simulation)");
    }
  };

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {actions.map((action) => (
        <button
          key={action.id}
          onClick={() => handleActionClick(action)}
          className="flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 transition-colors hover:bg-blue-100 dark:border-blue-900/30 dark:bg-blue-900/20 dark:text-blue-400 dark:hover:bg-blue-900/40"
        >
          {getIcon(action.type)}
          {action.label}
        </button>
      ))}
    </div>
  );
}

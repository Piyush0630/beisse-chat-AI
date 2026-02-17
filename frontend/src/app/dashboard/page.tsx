"use client";

import React from "react";
import { ArrowLeft, LayoutDashboard, BarChart3, Settings, Users, Bell } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              href="/"
              className="p-2 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-full transition-colors text-zinc-600 dark:text-zinc-400"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
                <LayoutDashboard className="h-6 w-6 text-blue-600" />
                Biesse Machine Dashboard
              </h1>
              <p className="text-zinc-500 dark:text-zinc-400">Monitor and manage your machining centers</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button className="p-2 text-zinc-500 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-lg transition-colors relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-zinc-50 dark:border-zinc-950"></span>
            </button>
            <button className="p-2 text-zinc-500 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-lg transition-colors">
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            { label: "Active Machines", value: "12", icon: LayoutDashboard, color: "text-blue-600", bg: "bg-blue-100" },
            { label: "Efficiency", value: "94.2%", icon: BarChart3, color: "text-green-600", bg: "bg-green-100" },
            { label: "Operators", value: "24", icon: Users, color: "text-purple-600", bg: "bg-purple-100" },
            { label: "Alerts", value: "3", icon: Bell, color: "text-red-600", bg: "bg-red-100" },
          ].map((stat, i) => (
            <div key={i} className="bg-white dark:bg-zinc-900 p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-lg ${stat.bg} ${stat.color}`}>
                  <stat.icon className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-sm text-zinc-500 dark:text-zinc-400 font-medium">{stat.label}</p>
                  <p className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
              <h2 className="font-semibold text-zinc-900 dark:text-zinc-100">Live Machine Status</h2>
              <button className="text-sm text-blue-600 font-medium hover:underline">View all</button>
            </div>
            <div className="p-0">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-xs uppercase text-zinc-500 bg-zinc-50 dark:bg-zinc-950 border-b border-zinc-100 dark:border-zinc-800">
                    <th className="px-6 py-3 font-medium">Machine ID</th>
                    <th className="px-6 py-3 font-medium">Model</th>
                    <th className="px-6 py-3 font-medium">Status</th>
                    <th className="px-6 py-3 font-medium">Load</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                  {[
                    { id: "ROVER-01", model: "Rover A 16", status: "Running", load: "78%" },
                    { id: "ROVER-02", model: "Rover B 2.0", status: "Idle", load: "0%" },
                    { id: "ROVER-03", model: "Rover Gold", status: "Warning", load: "92%" },
                    { id: "XNC-01", model: "XNC 2.5", status: "Running", load: "65%" },
                  ].map((m, i) => (
                    <tr key={i} className="text-sm text-zinc-600 dark:text-zinc-400">
                      <td className="px-6 py-4 font-medium text-zinc-900 dark:text-zinc-100">{m.id}</td>
                      <td className="px-6 py-4">{m.model}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          m.status === 'Running' ? 'bg-green-100 text-green-700' :
                          m.status === 'Idle' ? 'bg-zinc-100 text-zinc-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {m.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">{m.load}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-zinc-100 dark:border-zinc-800">
              <h2 className="font-semibold text-zinc-900 dark:text-zinc-100">Recent Alerts</h2>
            </div>
            <div className="p-6 space-y-6">
              {[
                { time: "2 mins ago", msg: "Low lubrication pressure on Rover-03", type: "error" },
                { time: "15 mins ago", msg: "Spindle speed variation detected on Rover-01", type: "warning" },
                { time: "1 hour ago", msg: "Maintenance scheduled for Rover-02 tomorrow", type: "info" },
              ].map((alert, i) => (
                <div key={i} className="flex gap-4">
                  <div className={`w-1 self-stretch rounded-full ${
                    alert.type === 'error' ? 'bg-red-500' :
                    alert.type === 'warning' ? 'bg-yellow-500' :
                    'bg-blue-500'
                  }`}></div>
                  <div>
                    <p className="text-xs text-zinc-400 mb-1">{alert.time}</p>
                    <p className="text-sm text-zinc-700 dark:text-zinc-300 font-medium">{alert.msg}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

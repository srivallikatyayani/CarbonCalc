"use client";

import { ReactNode } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
  score: number;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <main className="relative w-full h-screen overflow-hidden flex flex-col bg-[#03030c] bg-radial-[circle_at_center,_var(--tw-gradient-stops)] from-[#0a0a20] via-[#050512] to-[#030308]">
      {/* HUD Starfield Grid Layer */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none opacity-50" />
      
      {/* 2D HUD Overlay */}
      <div className="absolute inset-0 z-10 p-6 flex flex-col justify-between pointer-events-none">
        {/* Top Header */}
        <header className="flex justify-between items-center pointer-events-auto">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center font-bold text-lg shadow-[0_0_15px_rgba(16,185,129,0.5)]">
              C
            </div>
            <h1 className="text-xl font-bold tracking-widest text-white/90">
              CARBON<span className="text-emerald-400">CALC</span>
            </h1>
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex-1 flex w-full pointer-events-none">
          {children}
        </div>
      </div>
    </main>
  );
}

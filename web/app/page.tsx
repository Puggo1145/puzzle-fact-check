"use client"

import { Hero } from "./_components/hero";
import { NewsDisplay } from "./_components/news-display";
import { InputPanel } from "./_components/input-panel";
import { EventLog } from "@/components/agent/event-log";
import { Report } from "@/components/agent/report";
import { useAgentStore } from "@/lib/store";
import { cn } from "@/lib/utils";

export default function Home() {
  const { isRunning, finalReport } = useAgentStore();
  
  // Check if we're in active mode (either running or has a report)
  const isActive = isRunning || Boolean(finalReport);
  
  return (
    <div className="container min-h-screen flex flex-col py-10 relative">
      {/* News Display at the top */}
      <NewsDisplay />
      
      {/* Agent Execution Logs and Report */}
      <div className={cn("flex flex-col gap-6 flex-1", !isActive && "hidden")}>
        <EventLog />
        <Report />
      </div>
      
      {/* Spacer that takes up space when not running to push content to center */}
      <div className={cn("flex-1", isActive && "hidden")} />
      
      {/* Hero and Input Panel Container - centered when not running */}
      <div className={cn(
        "max-w-2xl w-full mx-auto transition-all duration-500 ease-in-out", 
        isActive ? "" : "flex-1 flex flex-col justify-center"
      )}>
        <Hero />
        <InputPanel />
      </div>
      
      {/* Bottom spacer */}
      <div className={cn("flex-1", isActive && "hidden")} />
    </div>
  );
}

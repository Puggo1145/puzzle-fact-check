"use client"

import { Hero } from "./_components/hero";
import { NewsDisplay } from "./_components/news-display";
import { InputPanel } from "./_components/input-panel/input-panel";
import { EventLog } from "@/components/agent/event-log";
import { Report } from "@/components/agent/report";
import { useAgentStore } from "@/stores/use-agent-store";
import { cn } from "@/lib/utils";

export default function Home() {
  const { status, finalReport, events } = useAgentStore();

  // Check if we're in active mode (not idle) or have results to show
  const isActive = status !== 'idle' || Boolean(finalReport) || events.length > 0;

  return (
    
    <div className="container relative w-full h-full flex flex-col items-center mx-auto">
      <div 
        className={cn(
          "w-full flex flex-col gap-6 transition-all duration-500 ease-in-out",
          isActive 
            ? "h-[80vh] overflow-y-auto" 
            : "h-0 overflow-hidden"
        )}
      >
        <NewsDisplay />
        <EventLog />
        <Report />
      </div>

      {/* Hero and Input Panel Container - always in the same place */}
      <div className={cn(
        " w-full transition-all duration-500 ease-in-out",
        isActive ? "mt-6" : "max-w-2xl flex-1 flex flex-col justify-center"
      )}>
        <Hero />
        <InputPanel />
      </div>
    </div>
  );
}

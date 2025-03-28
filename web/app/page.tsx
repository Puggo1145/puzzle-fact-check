"use client"

import { Hero } from "./_components/hero";
import { NewsDisplay } from "./_components/news-display";
import { InputPanel } from "./_components/input-panel/input-panel";
import { EventLog } from "@/components/agent/event-log";
import { Report } from "@/components/agent/report";
import { useAgentStore } from "@/lib/store";
import { cn } from "@/lib/utils";

export default function Home() {
  const { status, finalReport, events } = useAgentStore();

  // Check if we're in active mode (not idle) or have results to show
  const isActive = status !== 'idle' || Boolean(finalReport) || events.length > 0;

  return (
    <div className="container pt-0 h-full flex flex-col relative mx-auto">
      {/* Unified expandable box for fact-checking content */}
      <div 
        className={cn(
          "flex flex-col gap-6 transition-all duration-700 ease-in-out mb-6",
          isActive 
            ? "flex-1 overflow-y-auto pb-6 border-b" 
            : "h-[0vh] overflow-hidden"
        )}
      >
        <NewsDisplay />
        <EventLog />
        <Report />
      </div>

      {/* Hero and Input Panel Container - always in the same place */}
      <div className={cn(
        "max-w-2xl w-full mx-auto transition-all duration-500 ease-in-out",
        isActive ? "mb-12" : "flex-1 flex flex-col justify-center"
      )}>
        <Hero />
        <InputPanel />
      </div>
    </div>
  );
}

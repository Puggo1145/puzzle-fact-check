"use client"

import { Hero } from "./_components/hero";
import { NewsDisplay } from "./_components/news-display";
import { InputPanel } from "./_components/input-panel/input-panel";
import { EventLog } from "@/components/agent/event-log";
import { Report } from "@/components/agent/report";
import { useAgentStore } from "@/stores/use-agent-store";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { AnnouncementBadge } from "@/components/ui/announcement-badge";

export default function Home() {
  const { status, finalReport, events } = useAgentStore();

  // Check if we're in active mode (not idle) or have results to show
  const isActive = status !== 'idle' || Boolean(finalReport) || events.length > 0;

  return (
    <div className="relative max-w-[1000px] w-full h-full flex flex-col items-center mx-auto px-6">
      <ScrollArea
        className={cn(
          "w-full transition-all duration-500 ease-in-out",
          isActive
            ? "h-[calc(100svh-210px)] sm:h-[80svh]"
            : "h-[0]"
        )}
      >
        <NewsDisplay />
        <EventLog />
        <Report />
        <ScrollBar />
      </ScrollArea>

      {/* Hero and Input Panel Container - always in the same place */}
      <div className={cn(
        "w-full transition-all duration-500 ease-in-out mb-8",
        isActive ? "mt-6" : "max-w-2xl flex-1 flex flex-col justify-center"
      )}>
        <AnnouncementBadge />
        <Hero />
        <InputPanel />
      </div>
    </div>
  );
}

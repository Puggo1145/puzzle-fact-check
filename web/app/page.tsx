"use client"

import { Hero } from "./_components/hero";
import { NewsDisplay } from "./_components/news-display";
import { InputPanel } from "./_components/input-panel/input-panel";
import { EventLog } from "@/components/agent/event-log";
import { Report } from "@/components/agent/report";
import { useAgentStore } from "@/stores/use-agent-store";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
// import { AnnouncementBadge } from "@/components/ui/announcement-badge";

export default function Home() {
  const { status, result, events } = useAgentStore();
  const isActive = status !== 'idle' || Boolean(result.report) || events.length > 0;

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

      <div className={cn(
        "w-full transition-all duration-500 ease-in-out mb-8",
        isActive ? "mt-6" : "max-w-2xl flex-1 flex flex-col justify-center"
      )}>
        {/* <AnnouncementBadge className={isActive ? "opacity-0 h-0 pointer-events-none animate-none" : "opacity-100 animate-pulse"} /> */}
        <Hero className={isActive ? "opacity-0 h-0 pointer-events-none" : "opacity-100 mb-4"} />
        <InputPanel />
      </div>
    </div>
  );
}

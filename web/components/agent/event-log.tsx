'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useAgentStore } from '@/stores/use-agent-store';
import { EventItem } from './event-item';
import { ChevronDownIcon, ChevronUpIcon } from 'lucide-react';
import { Event } from '@/types/events';

export const EventLog: React.FC = () => {
  const { events, status, finalReport } = useAgentStore();
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  // Auto-scroll to bottom on new events
  useEffect(() => {
    if (scrollAreaRef.current && !isCollapsed) {
      const scrollContainer = scrollAreaRef.current;
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
  }, [events, isCollapsed]);
  
  // Auto-collapse when final report is available, but ensure it's expanded during running
  useEffect(() => {
    if (finalReport && status === 'completed') {
      setIsCollapsed(true);
    } else if (status === 'running' || status === 'interrupting') {
      setIsCollapsed(false);
    }
  }, [finalReport, status]);
  
  // If there are no events and we're in idle state with no report, don't show this component
  if (events.length === 0 && status === 'idle' && !finalReport) {
    return null;
  }
  
  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };
  
  return (
    <div className="mt-4 w-full max-h-[calc(100svh-330px)] flex flex-col overflow-hidden">
      <div 
        className="flex items-center justify-between p-3 border rounded-t-lg cursor-pointer"
        onClick={toggleCollapse}
      >
        <h2 className="text-sm font-semibold">核查过程</h2>
        <div className="flex items-center gap-2">
          <div className="text-xs text-muted-foreground">
            已执行 {events.length} 个步骤
          </div>
          {isCollapsed ? (
            <ChevronDownIcon className="size-4" />
          ) : (
            <ChevronUpIcon className="size-4" />
          )}
        </div>
      </div>
      
      {!isCollapsed && (
        <div 
          ref={scrollAreaRef}
          className="overflow-y-auto space-y-2 min-h-[200px] border border-t-0 rounded-b-lg p-3"
        >
          {events.length > 0 && events.map((event: Event, index: number) => (
            <EventItem key={index} event={event} />
          ))}
          {events.length === 0 && (
            <div className="text-center text-sm text-muted-foreground">
              正在连接到 Agent
            </div>
          )}
        </div>
      )}
    </div>
  );
}; 
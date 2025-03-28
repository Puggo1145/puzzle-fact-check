'use client';

import React, { useEffect, useRef } from 'react';
import { useAgentStore } from '@/lib/store';
import { EventItem } from './event-item';

export const EventLog: React.FC = () => {
  const { events, isRunning, finalReport } = useAgentStore();
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom on new events
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current;
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
  }, [events]);
  
  // If there are no events and neither running nor report, don't show this component
  if (events.length === 0 && !isRunning && !finalReport) {
    return null;
  }
  
  return (
    <div className="w-full flex flex-col flex-1">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-sm font-semibold">Agent 执行日志</h2>
        <div className="text-xs text-muted-foreground">
          {events.length} 个事件
        </div>
      </div>
      
      <div 
        ref={scrollAreaRef}
        className="flex-1 overflow-y-auto space-y-2 max-h-[calc(100vh-250px)]"
      >
        {events.length === 0 ? (
          <div className="h-32 flex items-center justify-center text-muted-foreground text-sm">
            {isRunning ? "加载中..." : "点击开始核查以查看 Agent 执行过程"}
          </div>
        ) : (
          events.map((event, index) => (
            <EventItem key={index} event={event} />
          ))
        )}
      </div>
    </div>
  );
}; 
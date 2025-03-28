'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useAgentStore } from '@/lib/store';
import { EventItem } from './event-item';
import { ChevronDownIcon, ChevronUpIcon } from 'lucide-react';

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
  
  // Auto-collapse when final report is available
  useEffect(() => {
    if (finalReport && status === 'completed') {
      setIsCollapsed(true);
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
    <div className="w-full flex-1 flex flex-col border rounded-lg overflow-hidden">
      <div 
        className="flex items-center justify-between p-3 border-b cursor-pointer"
        onClick={toggleCollapse}
      >
        <h2 className="text-sm font-semibold">Agent 执行日志</h2>
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
          className="flex-1 overflow-y-auto space-y-2 max-h-[calc(100vh-250px)] p-3"
        >
          {events.length === 0 ? (
            <div className="h-32 flex items-center justify-center text-muted-foreground text-sm">
              {status === 'running' || status === 'interrupting' ? "加载中..." : "点击开始核查以查看 Agent 执行过程"}
            </div>
          ) : (
            events.map((event, index) => (
              <EventItem key={index} event={event} />
            ))
          )}
        </div>
      )}
    </div>
  );
}; 
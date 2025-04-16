'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useAgentStore } from '@/stores/use-agent-store';
import { EventItem } from './event-item';
import { ChevronDownIcon, ChevronUpIcon, ArrowDownIcon } from 'lucide-react';
import { Event } from '@/types/events';

export const EventLog: React.FC = () => {
  const { events, status, result } = useAgentStore();
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const scrollTimerRef = useRef<NodeJS.Timeout | null>(null);
  const previousEventsLength = useRef(events.length);

  // Check if scroll position is at bottom
  const isAtBottom = () => {
    if (!scrollAreaRef.current) return true;
    
    const { scrollTop, scrollHeight, clientHeight } = scrollAreaRef.current;
    // Consider "at bottom" if within 20px of actual bottom
    return Math.abs(scrollHeight - scrollTop - clientHeight) < 20;
  };

  // Handle scroll events
  const handleScroll = () => {
    // Only set user scrolling if not already at bottom
    if (!isAtBottom()) {
      setIsUserScrolling(true);
      setShowScrollButton(true);
      
      // Reset the timer on each scroll event
      if (scrollTimerRef.current) {
        clearTimeout(scrollTimerRef.current);
      }
      
      scrollTimerRef.current = setTimeout(() => {
        if (isAtBottom()) {
          setIsUserScrolling(false);
          setShowScrollButton(false);
        }
      }, 30000); // 30 seconds
    } else {
      setIsUserScrolling(false);
      setShowScrollButton(false);
    }
  };

  // Scroll to bottom manually
  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: 'smooth',
      });
      setShowScrollButton(false);
      setIsUserScrolling(false);
    }
  };

  // Check for new events
  useEffect(() => {
    // If new events have been added and user isn't at bottom
    if (events.length > previousEventsLength.current && !isAtBottom()) {
      setShowScrollButton(true);
    }
    
    // Auto-scroll to bottom on new events if not user scrolling
    if (!isUserScrolling && !isCollapsed) {
      setTimeout(() => {
        if (scrollAreaRef.current) {
          scrollAreaRef.current.scrollTo({
            top: scrollAreaRef.current.scrollHeight,
            behavior: 'smooth',
          });
        }
      }, 100); // Small delay to ensure content is rendered
    }
    
    previousEventsLength.current = events.length;
  }, [events, isCollapsed, isUserScrolling]);

  // Set up scroll event listener
  useEffect(() => {
    const scrollContainer = scrollAreaRef.current;
    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handleScroll);
      return () => {
        scrollContainer.removeEventListener('scroll', handleScroll);
        if (scrollTimerRef.current) {
          clearTimeout(scrollTimerRef.current);
        }
      };
    }
  }, []);

  // Auto-collapse when final report is available, but ensure it's expanded during running
  useEffect(() => {
    if (result.report && status === 'completed') {
      setIsCollapsed(true);
    } else if (status === 'running' || status === 'interrupting') {
      setIsCollapsed(false);
    }
  }, [result.report, status]);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
    // Reset user scrolling state when toggling open
    if (isCollapsed) {
      setIsUserScrolling(false);
      setShowScrollButton(false);
    }
  };

  const isLastEvent = (index: number) => {
    return index === events.length - 1
      && ![
        'agent_start',
        'llm_decision',
        'task_complete',
        'task_interrupted',
        'error',
        'stream_closed'
      ].includes(events[index].event)
  };

  // If there are no events and we're in idle state with no report, don't show this component
  if (events.length === 0 && status === 'idle' && !result.report) {
    return null;
  }

  return (
    <div className="mt-4 w-full max-h-[calc(100svh-330px)] flex flex-col overflow-hidden relative">
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
          className="overflow-y-auto space-y-2 min-h-[200px] border border-t-0 rounded-b-lg p-3 scroll-smooth"
        >
          {events.length > 0 && events.map((event: Event, index: number) => (
            <EventItem
              key={index}
              event={event}
              isLastEvent={isLastEvent(index)}
            />
          ))}
          {events.length === 0 && (
            <div className="text-center text-sm text-muted-foreground">
              正在连接到 Agent...
            </div>
          )}
          
          {showScrollButton && (
            <button
              onClick={scrollToBottom}
              className="fixed bottom-8 right-8 bg-primary text-primary-foreground rounded-full p-2 shadow-md transition-opacity animate-in fade-in duration-300 hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary"
              aria-label="滚动到底部"
            >
              <ArrowDownIcon className="size-5" />
            </button>
          )}
        </div>
      )}
    </div>
  );
}; 
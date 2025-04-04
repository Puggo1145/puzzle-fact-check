import { API_BASE_URL } from '../constants/agent-default-config';
import type { AgentStatus } from '@/types/types';
import type { EventType, TypedEvent } from '@/types/events';


/**
 * Sets up an EventSource connection for Server-Sent Events
 */
export function setupEventSource(
  sessionId: string, 
  addEvent: <T extends EventType>(event: TypedEvent<T>) => void,
  setFinalReport: (report: string) => void,
  onStatusChange: (status: AgentStatus) => void
) {
  const eventSource = new EventSource(`${API_BASE_URL}/agents/${sessionId}/events`);
  
  // Timeout check variables
  let lastEventTime = Date.now();
  const TIMEOUT_DURATION = 180 * 1000; // 3 分钟无下一个事件响应则超时
  let isStreamClosed = false; // Add flag to track if stream is closed
  
  // Define function to update last event time
  const updateLastEventTime = () => {
    lastEventTime = Date.now();
  };
  
  // Define function to check for timeout
  const checkForTimeout = () => {
    // If stream is closed, don't check for timeout
    if (isStreamClosed) {
      console.log('Stream is closed, skipping timeout check');
      
      // Clear timeout checker if stream is closed
      if (timeoutCheckerId) {
        clearInterval(timeoutCheckerId);
      }
      return;
    }
    
    const currentTime = Date.now();
    const timeSinceLastEvent = currentTime - lastEventTime;
    
    // Check if timed out
    if (timeSinceLastEvent > TIMEOUT_DURATION) {
      console.log(`Timeout detected: No events for ${timeSinceLastEvent/1000} seconds`);
      
      // Clear timeout checker
      if (timeoutCheckerId) {
        clearInterval(timeoutCheckerId);
      }
      
      // Close EventSource connection
      eventSource.close();
      
      // Send timeout error event
      addEvent({
        event: 'error',
        data: { message: `请求超时: ${TIMEOUT_DURATION/1000}秒内没有收到新的事件` }
      } as TypedEvent<'error'>);
      
      // Send interrupted event
      setTimeout(() => {
        addEvent({
          event: 'task_interrupted',
          data: { message: `由于请求超时，任务已被中断` }
        } as TypedEvent<'task_interrupted'>);
      }, 100);
      
      // Interrupt backend agent
      fetch(`${API_BASE_URL}/agents/${sessionId}/interrupt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      }).catch(err => {
        console.error('Failed to interrupt agent after timeout:', err);
      });
      
      // Call the status change callback
      onStatusChange('interrupted');
    }
  };
  
  // Start timeout checker - check every 10 seconds
  const timeoutCheckerId = setInterval(checkForTimeout, 10000);
  
  // Add time update logic for all event types
  const setupEventTypeListener = <T extends EventType>(eventType: T) => {
    eventSource.addEventListener(eventType, (event) => {
      // Update last event time
      updateLastEventTime();

      if (!event.data) {
        return;
      }

      try {
        const data = JSON.parse(event.data);
        addEvent({ event: eventType, data } as TypedEvent<T>);
        
        if (eventType === 'write_fact_check_report_end' && data.report) {
          setFinalReport(data.report);
        }
      } catch(e) {
        console.error(`Error handling ${eventType} event:`, e);
      }
    });
  };
  
  // Set up listeners for all main event types
  const eventTypes: EventType[] = [
    'agent_start',
    'check_if_news_text_start', 'check_if_news_text_end',
    'extract_check_point_start', 'extract_check_point_end',
    'extract_basic_metadata_start', 'extract_basic_metadata_end',
    'extract_knowledge_start', 'extract_knowledge_end',
    'retrieve_knowledge_start', 'retrieve_knowledge_end',
    'search_agent_start', 'evaluate_current_status_start', 'evaluate_current_status_end',
    'tool_start', 'tool_end',
    'generate_answer_start', 'generate_answer_end',
    'evaluate_search_result_start', 'evaluate_search_result_end',
    'write_fact_check_report_start', 'write_fact_check_report_end',
    'llm_decision', 'task_complete', 'task_interrupted',
    'error',
  ];
  
  eventTypes.forEach(eventType => setupEventTypeListener(eventType));
  
  // Handle heartbeat events
  eventSource.addEventListener('heartbeat', () => {
    // Update last event time to prevent timeout
    updateLastEventTime();
  });
  
  // Handle stream_closed event
  eventSource.addEventListener('stream_closed', () => {
    // Mark stream as closed to prevent timeout checks
    isStreamClosed = true;
    
    // Clear timeout checker when stream is closed
    if (timeoutCheckerId) {
      clearInterval(timeoutCheckerId);
    }
    
    // Close the connection
    setTimeout(() => {
      eventSource.close();
    }, 100);
  });
  
  // Special handling for task_complete and task_interrupted events
  eventSource.addEventListener('task_complete', (event) => {
    updateLastEventTime();
    
    const data = JSON.parse(event.data);
    addEvent({ 
      event: 'task_complete', 
      data 
    } as TypedEvent<'task_complete'>);
    
    // Clear timeout checker when task is complete
    clearInterval(timeoutCheckerId);
    
    // Call the status change callback
    onStatusChange('completed');
    
    // Mark stream as closed to prevent error handling when connection closes
    isStreamClosed = true;
    
    // Close EventSource connection
    if (data && data.message === "核查任务完成") {
      setTimeout(() => {
        eventSource.close();
      }, 500);
    }
  });
  
  eventSource.addEventListener('task_interrupted', (event) => {
    updateLastEventTime();
    
    const data = JSON.parse(event.data);
    addEvent({ 
      event: 'task_interrupted', 
      data 
    } as TypedEvent<'task_interrupted'>);
    
    // Clear timeout checker when task is interrupted
    clearInterval(timeoutCheckerId);
    
    // Call the status change callback
    onStatusChange('interrupted');
    
    // Mark stream as closed to prevent error handling when connection closes
    isStreamClosed = true;
    
    // Close EventSource connection
    setTimeout(() => {
      eventSource.close();
    }, 500);
  });
  
  // Handle connection errors
  eventSource.addEventListener('error', (event) => {
    // Update last event time
    updateLastEventTime();
    
    // Only show error if the stream isn't intentionally closed
    // This prevents showing error when connection closes normally after task_complete
    if (!isStreamClosed) {
      console.error('EventSource encountered an error:', event);
      
      const DEFAULT_ERROR_MESSAGE = '与服务器的连接中断，请检查您的网络连接或稍后再试。';
      let errorMessage = DEFAULT_ERROR_MESSAGE;
      
      // Check if the error is from the response
      if (event instanceof MessageEvent && event.data) {
        try {
          const data = JSON.parse(event.data);
          
          if (data && data.message) {
            const msg = data.message;
            
            if (msg.includes('quota')) {
              errorMessage = '模型额度已用尽，请稍后再试或联系管理员。';
            } else if (msg.includes('Rate limit')) {
              errorMessage = '请求速率限制，请稍后再试。';
            } else if (msg.includes('data_inspection_failed')) {
              errorMessage = '核查内容触发模型敏感内容封控，请更换核查内容或模型后重试'
            } else if (msg.includes('not available in your region')) {
              errorMessage = '所选模型在当前区域不可用，请更换模型后重试。';
            } else if (msg.includes('model is currently overloaded')) {
              errorMessage = '模型目前负载过高，请稍后再试。';
            } else {
              errorMessage = `服务器错误: ${msg}`;
            }
          }
        } catch {
          // If not JSON, check for common error patterns in the string
          const errorString = event.data.toString();
          if (errorString.includes('429')) {
            errorMessage = '请求过于频繁，请稍后再试。';
          } else if (errorString.includes('quota') || errorString.includes('exceeded')) {
            errorMessage = '模型配额已用尽，请稍后再试或联系管理员。';
          } else if (errorString.includes('overloaded')) {
            errorMessage = '模型目前负载过高，请稍后再试。';
          }
        }
      }
      
      // Add error event to the log
      addEvent({
        event: 'error',
        data: { 
          message: errorMessage,
        }
      } as TypedEvent<'error'>);
      
      // Update status to interrupted rather than staying in running
      onStatusChange('interrupted');
    }
    
    // Close the connection if not already closed
    if (eventSource.readyState !== EventSource.CLOSED) {
      eventSource.close();
    }
    
    // Manually dispatch stream_closed event if not already marked as closed
    if (!isStreamClosed) {
      isStreamClosed = true;
      if (timeoutCheckerId) {
        clearInterval(timeoutCheckerId);
      }
      addEvent({
        event: 'stream_closed',
        data: {}
      } as unknown as TypedEvent<'stream_closed'>);
    }
  });
  
  eventSource.addEventListener('close', () => {
    console.log('EventSource close event triggered');
    
    // Mark stream as closed to prevent timeout checks
    isStreamClosed = true;
    
    // Clear the timeout checker
    if (timeoutCheckerId) {
      clearInterval(timeoutCheckerId);
    }
  });
  
  return eventSource;
}

/**
 * Process the received event and update state accordingly
 */
export function processEvent<T extends EventType>(event: TypedEvent<T>): { status: AgentStatus; sessionId: null; eventSource: null } | null {
  // If it's a completion event, update to completed status
  if (event.event === 'task_complete') {
    return {
      status: 'completed',
      sessionId: null,
      eventSource: null
    };
  }
  
  // If it's an interruption event, update to interrupted status
  if (event.event === 'task_interrupted') {
    return {
      status: 'interrupted',
      sessionId: null,
      eventSource: null
    };
  }
  
  // Special handling for error events
  if (event.event === 'error') {
    return {
      status: 'interrupted',
      sessionId: null,
      eventSource: null
    };
  }
  
  return null;
} 
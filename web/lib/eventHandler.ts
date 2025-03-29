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
  
  // Define function to update last event time
  const updateLastEventTime = () => {
    lastEventTime = Date.now();
  };
  
  // Define function to check for timeout
  const checkForTimeout = () => {
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
  
  eventSource.addEventListener('heartbeat', () => {
    // Keep connection alive
    updateLastEventTime();
  });
  
  // Add time update logic for all event types
  const setupEventTypeListener = <T extends EventType>(eventType: T) => {
    eventSource.addEventListener(eventType, (event) => {
      // Update last event time
      updateLastEventTime();
      
      // Previous event handling logic
      try {
        const data = JSON.parse(event.data);
        addEvent({ event: eventType, data } as TypedEvent<T>);
        
        // Handle special report type events
        if (eventType === 'write_fact_checking_report_end' && data.report) {
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
    'extract_check_point_start', 'extract_check_point_end',
    'extract_basic_metadata_start', 'extract_basic_metadata_end',
    'extract_knowledge_start', 'extract_knowledge_end',
    'retrieve_knowledge_start', 'retrieve_knowledge_end',
    'search_agent_start', 'evaluate_current_status_start', 'evaluate_current_status_end',
    'tool_start', 'tool_result',
    'generate_answer_start', 'generate_answer_end',
    'evaluate_search_result_start', 'evaluate_search_result_end',
    'write_fact_checking_report_start', 'write_fact_checking_report_end',
    'llm_decision', 'task_complete', 'task_interrupted',
  ];
  
  eventTypes.forEach(eventType => setupEventTypeListener(eventType));
  
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
    
    // Close EventSource connection
    setTimeout(() => {
      eventSource.close();
    }, 500);
  });
  
  // Error event
  eventSource.addEventListener('error', (event: MessageEvent) => {
    // Error events also update last event time
    updateLastEventTime();
    
    if (event.data) {
      try {
        const data = JSON.parse(event.data);
        addEvent({ 
          event: 'error', 
          data 
        } as TypedEvent<'error'>);
        
        // Check if it's a model error or a validation error, if so close the connection
        const errorMessage = data.message || '';
        if (
          errorMessage.includes('OpenAI API') || 
          errorMessage.includes('模型API错误') || 
          errorMessage.includes('配额') || 
          errorMessage.includes('速率限制') ||
          errorMessage.includes('validation error') ||
          errorMessage.includes('pydantic')
        ) {
          console.log('Model API error or validation error in SSE, closing connection');
          // Clear timeout checker
          clearInterval(timeoutCheckerId);
          
          eventSource.close();
          
          // Add interrupted event after error event to ensure UI state updates correctly
          setTimeout(() => {
            addEvent({ 
              event: 'task_interrupted', 
              data: { message: errorMessage.includes('validation error') ? 
                '由于数据验证错误，任务已被中断' : 
                '由于模型API错误，任务已被中断' } 
            } as TypedEvent<'task_interrupted'>);
            
            // Call the status change callback
            onStatusChange('interrupted');
          }, 100);
        }
      } catch {
        addEvent({
          event: 'error',
          data: { message: 'SSE 解析错误: ' + (event.data || '未知错误') }
        } as TypedEvent<'error'>);
      }
    } else {
      // EventSource connection error, could be network issues or server closed the connection
      console.error('SSE connection error without data');
      
      // Clear timeout checker
      clearInterval(timeoutCheckerId);
      
      // Add error event
      addEvent({
        event: 'error',
        data: { message: 'SSE 连接错误，任务可能已被终止' }
      } as TypedEvent<'error'>);
      
      // Add interrupted event to update UI state
      setTimeout(() => {
        addEvent({ 
          event: 'task_interrupted', 
          data: { message: '连接中断，任务已终止' } 
        } as TypedEvent<'task_interrupted'>);
        
        // Call the status change callback
        onStatusChange('interrupted');
      }, 100);
    }
  });
  
  eventSource.addEventListener('close', () => {
    clearInterval(timeoutCheckerId);
  });
  
  eventSource.addEventListener('heartbeat', () => {
    updateLastEventTime();
  });
  
  return eventSource;
}

/**
 * Process the received event and update state accordingly
 */
export function processEvent<T extends EventType>(event: TypedEvent<T>): { status: AgentStatus; sessionId: null; eventSource: null } | null {
  // If it's a completion or interruption event, update the running status and close the event stream
  if (event.event === 'task_complete' || event.event === 'task_interrupted') {
    return {
      status: event.event === 'task_complete' ? 'completed' : 'interrupted',
      sessionId: null,
      eventSource: null
    };
  }
  
  // Special handling for error events
  if (event.event === 'error') {
    // Safe type assertion since we've already checked event.event === 'error'
    const errorData = event.data as { message: string } | undefined;
    const errorMessage = errorData?.message || '';
    
    // Check if it's a model API related error or a validation error
    if (
      errorMessage.includes('OpenAI API') || 
      errorMessage.includes('模型API错误') || 
      errorMessage.includes('配额') || 
      errorMessage.includes('速率限制') ||
      errorMessage.includes('validation error') ||
      errorMessage.includes('pydantic')
    ) {
      // For model API errors or validation errors, treat it like an interruption
      return {
        status: 'interrupted',
        sessionId: null,
        eventSource: null
      };
    }
  }
  
  return null;
} 
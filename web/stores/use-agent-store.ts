import { create } from 'zustand';
import { 
  AVAILABLE_MODELS, 
  DEFAULT_MAIN_AGENT_CONFIG,
  DEFAULT_METADATA_EXTRACTOR_CONFIG,
  DEFAULT_SEARCHER_CONFIG
} from '../constants/agent-default-config';
import * as api from '@/api/agent-session';
import { setupEventSource as setupEventSourceHandler, processEvent } from '@/lib/eventHandler';
import type { AgentState } from '../types/types';
import type { Event, EventType, TypedEvent } from '../types/events';

export const useAgentStore = create<AgentState>((set, get) => ({
  sessionId: null,
  status: 'idle',
  events: [],
  finalReport: '',
  newsText: '',
  // Agent 默认配置
  mainAgentConfig: DEFAULT_MAIN_AGENT_CONFIG,
  metadataExtractorConfig: DEFAULT_METADATA_EXTRACTOR_CONFIG,
  searcherConfig: DEFAULT_SEARCHER_CONFIG,
  selectedTools: [],
  availableModels: AVAILABLE_MODELS,
  eventSource: null,
  setNewsText: (text: string) => set({ newsText: text }),
  setMainAgentConfig: (config) => set(state => ({
    mainAgentConfig: { ...state.mainAgentConfig, ...config }
  })),
  setMetadataExtractorConfig: (config) => set(state => ({
    metadataExtractorConfig: { ...state.metadataExtractorConfig, ...config }
  })),
  setSearcherConfig: (config) => set(state => ({
    searcherConfig: { ...state.searcherConfig, ...config }
  })),
  setSelectedTools: (tools) => set({ selectedTools: tools }),

  // APIs
  createAndRunAgent: async () => {
    const {
      newsText, 
      mainAgentConfig, 
      metadataExtractorConfig, 
      searcherConfig,
      selectedTools
    } = get();
    
    // Don't start if already running or if there's no input
    if (get().status !== 'idle' || !newsText.trim()) {
      return;
    }
    
    // Reset state before starting
    set({
      events: [],
      status: 'running',
      finalReport: '',
    });
    
    try {
      const data = await api.createAndRunAgent(
        newsText,
        mainAgentConfig,
        metadataExtractorConfig,
        searcherConfig,
      );
      
      // Update sessionId
      set({ sessionId: data.session_id });
      
      // Set up EventSource connection
      const eventSource = setupEventSourceHandler(
        data.session_id,
        get().addEvent,
        get().setFinalReport,
        (status) => {
          // This callback is called when the status changes to completed or interrupted
          set({
            status,
            sessionId: null,
            eventSource: null
          });
        }
      );
      
      set({ eventSource });
      
    } catch (error) {
      console.error('Error starting agent:', error);
      
      // Check if error is due to backend service unavailable or network error
      let errorMessage;
      if (
        error instanceof TypeError && error.message.includes('Failed to fetch') ||
        error instanceof DOMException && error.name === 'AbortError' ||
        error instanceof Error && error.message.includes('NetworkError') ||
        error instanceof Error && error.message.includes('Network request failed') ||
        error instanceof Error && error.message.includes('Failed to fetch') ||
        error instanceof Error && error.message.includes('Network error')
      ) {
        errorMessage = '无法连接到 Puzzle 服务器，请稍后再试（Puzzle 是一个个人实验项目，计算资源较少，请谅解）';
      } else {
        errorMessage = error instanceof Error ? error.message : String(error);
      }
      
      set({ 
        status: 'idle',
        events: [...get().events, {
          event: 'error',
          data: { message: errorMessage }
        } as TypedEvent<'error'>]
      });
    }
  },

  interruptAgent: async () => {
    const { sessionId } = get();
    
    if (!sessionId) {
      return;
    }
    
    try {
      set({ status: 'interrupting' });
      
      get().addEvent({
        event: 'task_interrupted',
        data: { message: '正在尝试中断任务...' }
      } as TypedEvent<'task_interrupted'>);
      
      await api.interruptAgent(sessionId);
      
      // Close current EventSource connection
      get().closeEventSource();
      
      // Always add interrupt success message, even if user already clicked return
      get().addEvent({
        event: 'task_interrupted',
        data: { message: '任务已被中断' }
      } as TypedEvent<'task_interrupted'>);
      
      // Only update status if it's still 'interrupting'
      const currentStatus = get().status;
      if (currentStatus === 'interrupting') {
        set({ 
          status: 'interrupted',
          sessionId: null
        });
      }
      
    } catch (error) {
      console.error('中断任务失败:', error);
      get().addEvent({
        event: 'error',
        data: { message: `中断任务失败: ${error instanceof Error ? error.message : String(error)}` }
      } as TypedEvent<'error'>);
      // If interruption fails and status is still 'interrupting', restore to 'running'
      const currentStatus = get().status;
      if (currentStatus === 'interrupting') {
        set({ status: 'running' });
      }
    }
  },
  
  resetState: () => {
    // Close existing EventSource connection
    get().closeEventSource();
    
    set({
      sessionId: null,
      status: 'idle',
      events: [],
      finalReport: '',
      eventSource: null,
    });
  },
  
  addEvent: <T extends EventType>(event: TypedEvent<T>) => set((state) => {
    const eventWithTimestamp = { ...event, timestamp: Date.now() };
    
    // Process the event to determine if state needs to be updated
    const stateUpdate = processEvent(eventWithTimestamp);
    
    if (stateUpdate) {
      // If stateUpdate is not null, apply state changes along with the new event
      return {
        status: stateUpdate.status,
        sessionId: stateUpdate.sessionId,
        eventSource: stateUpdate.eventSource,
        events: [...state.events, eventWithTimestamp]
      };
    }
    
    // Default just adds the event
    return {
      events: [...state.events, eventWithTimestamp]
    };
  }),
  
  setFinalReport: (report: string) => set({ finalReport: report }),
  
  closeEventSource: () => {
    const eventSource = get().eventSource;
    if (eventSource) {
      // Manually trigger close event before closing to ensure timeout checker is cleared
      const closeEvent = new Event('close');
      eventSource.dispatchEvent(closeEvent);
      
      // Close connection
      eventSource.close();
      set({ eventSource: null });
    }
  },
})); 
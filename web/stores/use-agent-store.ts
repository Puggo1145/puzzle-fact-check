import { create } from 'zustand';
import { AVAILABLE_MODELS, CONFIG_PRESETS } from '../constants/agent-default-config';
import * as api from '@/api/agent-session';
import { setupEventSource as setupEventSourceHandler, processEvent } from '@/lib/event-handler';
import type { AgentState, Verdict } from '../types/types';
import type { Event } from '../types/events';

export const useAgentStore = create<AgentState>((set, get) => ({
  sessionId: null,
  status: 'idle',
  events: [],
  result: {
    report: undefined,
    verdict: undefined
  },
  newsText: '',
  // Agent 默认配置
  mainAgentConfig: CONFIG_PRESETS[0].mainConfig,
  metadataExtractorConfig: CONFIG_PRESETS[0].metadataConfig,
  searcherConfig: CONFIG_PRESETS[0].searchConfig,
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
      result: {
        report: undefined,
        verdict: undefined
      },
    });

    // add selected tools to search agent config
    searcherConfig.selectedTools = selectedTools
    
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
        get().setResult,
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
        errorMessage = 'Unable to connect to Puzzle server. Please try again later (Puzzle is a personal experiment project, with limited computing resources, please understand)';
      } else {
        errorMessage = error instanceof Error ? error.message : String(error);
      }
      
      // Add error event
      get().addEvent({
        event: 'error',
        data: { message: errorMessage }
      });
      
      // Then transition to interrupted (not directly to idle)
      set({ status: 'interrupted' });
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
        data: { message: 'Trying to interrupt task...' }
      });
      
      await api.interruptAgent(sessionId);
      
      // Close current EventSource connection
      get().closeEventSource();
      
      // Always add interrupt success message, even if user already clicked return
      get().addEvent({
        event: 'task_interrupted',
        data: { message: 'Task Interrupted' }
      });
      
      // Only update status if it's still 'interrupting'
      const currentStatus = get().status;
      if (currentStatus === 'interrupting') {
        set({ 
          status: 'interrupted',
          sessionId: null
        });
      }
      
    } catch (error) {
      console.error('Failed to interrupt task:', error);
      get().addEvent({
        event: 'error',
        data: { message: `Failed to interrupt task: ${error instanceof Error ? error.message : String(error)}` }
      });
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
      result: {
        report: undefined,
        verdict: undefined
      },
      eventSource: null,
    });
  },
  
  addEvent: (event: Event) => set((state) => {
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
  
  setResult: (report: string, verdict: Verdict) => {
    set({ 
      result: { 
        report, 
        verdict 
      } 
    });
  },
  
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

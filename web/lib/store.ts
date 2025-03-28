import { create } from 'zustand';

// Define the available models
export interface ModelOption {
  id: string;
  name: string;
  provider: string;
}

// Agent configuration interface
export interface AgentConfig {
  modelName: string;
  modelProvider: string;
  maxSearchTokens: number; // Only used by the searcher agent
  maxRetries: number; // Only used by the main agent
}

// Define the possible agent statuses
export type AgentStatus = 'idle' | 'running' | 'interrupting' | 'interrupted' | 'completed';

export type EventType = 
  | 'agent_created'
  | 'run_started'
  | 'extract_check_point_start'
  | 'extract_check_point_end'
  | 'extract_basic_metadata_start'
  | 'extract_basic_metadata_end'
  | 'extract_knowledge_start'
  | 'extract_knowledge_end'
  | 'retrieve_knowledge_start'
  | 'retrieve_knowledge_end'
  | 'search_agent_start'
  | 'evaluate_status_start'
  | 'status_evaluation_end'
  | 'tool_start'
  | 'tool_result'
  | 'generate_answer_start'
  | 'generate_answer_end'
  | 'evaluate_search_result_start'
  | 'evaluate_search_result_end'
  | 'write_fact_checking_report_start'
  | 'write_fact_checking_report_end'
  | 'llm_decision'
  | 'task_complete'
  | 'task_interrupted'
  | 'error';

export interface Event {
  event: EventType;
  data: any;
  timestamp?: number;
}

interface AgentState {
  sessionId: string | null;
  status: AgentStatus;
  events: Event[];
  finalReport: string;
  newsText: string;
  // Agent configurations
  mainAgentConfig: AgentConfig;
  metadataExtractorConfig: AgentConfig;
  searcherConfig: AgentConfig;
  // Available models
  availableModels: ModelOption[];
  // EventSource
  eventSource: EventSource | null;
  // Actions
  setNewsText: (text: string) => void;
  setMainAgentConfig: (config: Partial<AgentConfig>) => void;
  setMetadataExtractorConfig: (config: Partial<AgentConfig>) => void;
  setSearcherConfig: (config: Partial<AgentConfig>) => void;
  createAgent: () => Promise<void>;
  startFactCheck: () => Promise<void>;
  interruptAgent: () => Promise<void>;
  resetState: () => void;
  addEvent: (event: Event) => void;
  setFinalReport: (report: string) => void;
  closeEventSource: () => void;
  createAndRunAgent: () => Promise<void>;
}

// API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Available models
const models: ModelOption[] = [
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai' },
  { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', provider: 'openai' },
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai' },
  { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'anthropic' },
  { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'anthropic' },
  { id: 'claude-3-haiku', name: 'Claude 3 Haiku', provider: 'anthropic' },
];

// Define default configurations
const defaultAgentConfig: AgentConfig = {
  modelName: 'gpt-4o',
  modelProvider: 'openai',
  maxSearchTokens: 10000,
  maxRetries: 3
};

export const useAgentStore = create<AgentState>((set, get) => ({
  sessionId: null,
  status: 'idle',
  events: [],
  finalReport: '',
  newsText: '最近有网络流传说法称，2025 年初，美国共和党议员Riley Moore通过了一项新法案，将禁止中国公民以学生身份来美国。这项法案会导致每年大约30万中国学生将无法获得F、J、M类签证，从而无法到美国学习或参与学术交流。',
  
  // Agent configurations with defaults
  mainAgentConfig: { ...defaultAgentConfig },
  metadataExtractorConfig: { ...defaultAgentConfig },
  searcherConfig: { ...defaultAgentConfig, maxSearchTokens: 20000 },
  
  // Available models
  availableModels: models,
  
  setNewsText: (text: string) => set({ newsText: text }),
  
  setMainAgentConfig: (config: Partial<AgentConfig>) => set(state => ({
    mainAgentConfig: { ...state.mainAgentConfig, ...config }
  })),
  
  setMetadataExtractorConfig: (config: Partial<AgentConfig>) => set(state => ({
    metadataExtractorConfig: { ...state.metadataExtractorConfig, ...config }
  })),
  
  setSearcherConfig: (config: Partial<AgentConfig>) => set(state => ({
    searcherConfig: { ...state.searcherConfig, ...config }
  })),
  
  createAgent: async () => {
    const { mainAgentConfig, searcherConfig } = get();
    
    // 关闭现有的EventSource连接
    get().closeEventSource();
    
    try {
      const response = await fetch(`${API_BASE_URL}/agents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model_name: mainAgentConfig.modelName,
          model_provider: mainAgentConfig.modelProvider,
          config: {
            main_agent: {
              max_retries: mainAgentConfig.maxRetries
            },
            searcher: {
              max_search_tokens: searcherConfig.maxSearchTokens
            }
          }
        })
      });
      
      const data = await response.json();
      
      set({ 
        sessionId: data.session_id,
      });
      
      get().addEvent({
        event: 'agent_created',
        data: { message: `Agent 创建成功: ${data.session_id}` }
      });
      
      // Setup event source
      setupEventSource(get().sessionId as string, get().addEvent, get().setFinalReport);
      
    } catch (error) {
      console.error('创建 Agent 失败:', error);
      get().addEvent({
        event: 'error',
        data: { message: `创建 Agent 失败: ${error instanceof Error ? error.message : String(error)}` }
      });
    }
  },
  
  startFactCheck: async () => {
    const { 
      sessionId, 
      newsText, 
      mainAgentConfig, 
      metadataExtractorConfig, 
      searcherConfig 
    } = get();
    
    if (!sessionId) {
      get().addEvent({
        event: 'error',
        data: { message: 'Session ID not found. Please create an agent first.' }
      });
      return;
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/agents/${sessionId}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          news_text: newsText,
          config: {
            main_agent: {
              model_name: mainAgentConfig.modelName,
              model_provider: mainAgentConfig.modelProvider,
              max_retries: mainAgentConfig.maxRetries
            },
            metadata_extractor: {
              model_name: metadataExtractorConfig.modelName,
              model_provider: metadataExtractorConfig.modelProvider
            },
            searcher: {
              model_name: searcherConfig.modelName,
              model_provider: searcherConfig.modelProvider,
              max_search_tokens: searcherConfig.maxSearchTokens
            }
          }
        })
      });
      
      await response.json();
      
      set({ status: 'running' });
      
      get().addEvent({
        event: 'run_started',
        data: { message: '开始执行核查流程' }
      });
      
    } catch (error) {
      console.error('启动核查失败:', error);
      get().addEvent({
        event: 'error',
        data: { message: `启动核查失败: ${error instanceof Error ? error.message : String(error)}` }
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
      });
      
      const response = await fetch(`${API_BASE_URL}/agents/${sessionId}/interrupt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const responseData = await response.json();
      
      // 关闭当前的EventSource连接
      get().closeEventSource();
      
      // 总是添加中断成功的消息，即使用户已经点击了返回
      get().addEvent({
        event: 'task_interrupted',
        data: { message: '任务已被中断' }
      });
      
      // 只有在状态仍为interrupting时才更新状态
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
      });
      // 如果中断失败且状态仍为interrupting，恢复为运行状态
      const currentStatus = get().status;
      if (currentStatus === 'interrupting') {
        set({ status: 'running' });
      }
    }
  },
  
  resetState: () => {
    // 关闭现有的EventSource连接
    get().closeEventSource();
    
    set({
      sessionId: null,
      status: 'idle',
      events: [],
      finalReport: '',
      eventSource: null,
    });
  },
  
  addEvent: (event: Event) => set((state) => {
    // 如果是任务完成或中断事件，更新运行状态并关闭事件流
    if (event.event === 'task_complete' || event.event === 'task_interrupted') {
      // 关闭EventSource连接
      const eventSource = get().eventSource;
      if (eventSource) {
        console.log('Closing EventSource connection due to task completion');
        eventSource.close();
      }
      
      const newStatus = event.event === 'task_complete' ? 'completed' : 'interrupted';
      
      return {
        events: [...state.events, { ...event, timestamp: Date.now() }],
        status: newStatus,
        eventSource: null,
        sessionId: null // Also clear sessionId when task completes or is interrupted
      };
    }
    
    return {
      events: [...state.events, { ...event, timestamp: Date.now() }]
    };
  }),
  
  setFinalReport: (report: string) => set({ finalReport: report }),
  
  eventSource: null,
  
  closeEventSource: () => {
    const eventSource = get().eventSource;
    if (eventSource) {
      eventSource.close();
      set({ eventSource: null });
    }
  },
  
  createAndRunAgent: async () => {
    const { 
      newsText, 
      mainAgentConfig, 
      metadataExtractorConfig, 
      searcherConfig 
    } = get();
    
    // 关闭现有的EventSource连接
    get().closeEventSource();
    
    try {
      const response = await fetch(`${API_BASE_URL}/fact-check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          news_text: newsText,
          config: {
            model_name: mainAgentConfig.modelName,
            model_provider: mainAgentConfig.modelProvider,
            main_agent: {
              max_retries: mainAgentConfig.maxRetries
            },
            metadata_extractor: {
              model_name: metadataExtractorConfig.modelName,
              model_provider: metadataExtractorConfig.modelProvider
            },
            searcher: {
              model_name: searcherConfig.modelName,
              model_provider: searcherConfig.modelProvider,
              max_search_tokens: searcherConfig.maxSearchTokens
            }
          }
        })
      });
      
      const data = await response.json();
      
      set({ 
        sessionId: data.session_id,
        status: 'running'
      });
      
      // Setup event source
      setupEventSource(data.session_id, get().addEvent, get().setFinalReport);
      
      get().addEvent({
        event: 'run_started',
        data: { message: '开始执行核查流程' }
      });
      
    } catch (error) {
      console.error('启动核查失败:', error);
      get().addEvent({
        event: 'error',
        data: { message: `启动核查失败: ${error instanceof Error ? error.message : String(error)}` }
      });
    }
  }
}));

// Setup EventSource for SSE
function setupEventSource(
  sessionId: string, 
  addEvent: (event: Event) => void,
  setFinalReport: (report: string) => void
) {
  const eventSource = new EventSource(`${API_BASE_URL}/agents/${sessionId}/events`);
  
  // 保存到全局状态
  useAgentStore.setState({ eventSource });
  
  eventSource.addEventListener('heartbeat', () => {
    // Keep connection alive
  });
  
  // Extract check point events
  eventSource.addEventListener('extract_check_point_start', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'extract_check_point_start', data });
  });
  
  eventSource.addEventListener('extract_check_point_end', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'extract_check_point_end', data });
  });
  
  // Metadata extractor events
  eventSource.addEventListener('extract_basic_metadata_start', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'extract_basic_metadata_start', data });
  });
  
  eventSource.addEventListener('extract_basic_metadata_end', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'extract_basic_metadata_end', data });
  });
  
  eventSource.addEventListener('extract_knowledge_start', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'extract_knowledge_start', data });
  });
  
  eventSource.addEventListener('extract_knowledge_end', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'extract_knowledge_end', data });
  });
  
  eventSource.addEventListener('retrieve_knowledge_start', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'retrieve_knowledge_start', data });
  });
  
  eventSource.addEventListener('retrieve_knowledge_end', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'retrieve_knowledge_end', data });
  });
  
  // Search agent events
  eventSource.addEventListener('search_agent_start', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'search_agent_start', data });
  });
  
  eventSource.addEventListener('evaluate_status_start', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'evaluate_status_start', data });
  });
  
  eventSource.addEventListener('status_evaluation_end', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'status_evaluation_end', data });
  });
  
  eventSource.addEventListener('tool_start', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'tool_start', data });
  });
  
  eventSource.addEventListener('tool_result', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'tool_result', data });
  });
  
  eventSource.addEventListener('generate_answer_start', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'generate_answer_start', data });
  });
  
  eventSource.addEventListener('generate_answer_end', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'generate_answer_end', data });
  });
  
  // Evaluation events
  eventSource.addEventListener('evaluate_search_result_start', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'evaluate_search_result_start', data });
  });
  
  eventSource.addEventListener('evaluate_search_result_end', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'evaluate_search_result_end', data });
  });
  
  // Report writing events
  eventSource.addEventListener('write_fact_checking_report_start', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'write_fact_checking_report_start', data });
  });
  
  eventSource.addEventListener('write_fact_checking_report_end', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'write_fact_checking_report_end', data });
    
    if (data.report) {
      setFinalReport(data.report);
    }
  });
  
  // LLM decision event
  eventSource.addEventListener('llm_decision', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'llm_decision', data });
  });
  
  // Task completion event
  eventSource.addEventListener('task_complete', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'task_complete', data });
    // Close the event source after task completion
    if (data && data.message === "核查任务完成") {
      setTimeout(() => {
        // Allow a bit of time for the event to be processed
        useAgentStore.getState().closeEventSource();
      }, 500);
    }
  });
  
  // Task interrupted event
  eventSource.addEventListener('task_interrupted', (event) => {
    const data = JSON.parse(event.data);
    addEvent({ event: 'task_interrupted', data });
    // Close the event source after task interruption
    setTimeout(() => {
      // Allow a bit of time for the event to be processed
      useAgentStore.getState().closeEventSource();
    }, 500);
  });
  
  // Error event
  eventSource.addEventListener('error', (event: MessageEvent) => {
    if (event.data) {
      try {
        const data = JSON.parse(event.data);
        addEvent({ event: 'error', data });
      } catch (e) {
        addEvent({
          event: 'error',
          data: { message: 'SSE 解析错误: ' + (event.data || '未知错误') }
        });
      }
    } else {
      addEvent({
        event: 'error',
        data: { message: 'SSE 连接错误' }
      });
    }
  });
  
  return eventSource;
} 
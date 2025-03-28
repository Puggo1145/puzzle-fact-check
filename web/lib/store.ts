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
const API_BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

// Available models
const models: ModelOption[] = [
  // OpenAI models
  { id: 'chatgpt-4o-latest', name: 'GPT-4o Latest', provider: 'openai' },
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'openai' },
  
  // Qwen models
  { id: 'qwq-plus-latest', name: 'QWQ Plus Latest', provider: 'qwen' },
  { id: 'qwen-plus-latest', name: 'Qwen Plus Latest', provider: 'qwen' },
  { id: 'qwen-turbo', name: 'Qwen Turbo', provider: 'qwen' },
  
  // DeepSeek models
  { id: 'deepseek-reasoner', name: 'DeepSeek R1', provider: 'deepseek' },
  { id: 'deepseek-chat', name: 'DeepSeek V3', provider: 'deepseek' },
];

// Define default configurations
const defaultAgentConfig: AgentConfig = {
  modelName: 'chatgpt-4o-latest',
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
  mainAgentConfig: { ...defaultAgentConfig, modelName: 'qwq-plus-latest', modelProvider: 'qwen' },
  metadataExtractorConfig: { ...defaultAgentConfig, modelName: 'qwen-plus-latest', modelProvider: 'qwen' },
  searcherConfig: { ...defaultAgentConfig, modelName: 'deepseek-chat', modelProvider: 'deepseek', maxSearchTokens: 20000 },
  
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
    
    // 特殊处理错误事件
    if (event.event === 'error') {
      const errorMessage = event.data?.message || '';
      
      // 检查是否是模型API相关错误
      if (
        errorMessage.includes('OpenAI API') || 
        errorMessage.includes('模型API错误') || 
        errorMessage.includes('配额') || 
        errorMessage.includes('速率限制')
      ) {
        // 对于模型API错误，自动切换到interrupted状态
        // 这样用户界面会显示中断状态而不是错误状态
        console.log('Model API error detected, forcing interrupt status');
        
        // 关闭EventSource连接
        const eventSource = get().eventSource;
        if (eventSource) {
          console.log('Closing EventSource connection due to model error');
          eventSource.close();
        }
        
        return {
          events: [...state.events, { ...event, timestamp: Date.now() }],
          status: 'interrupted',
          eventSource: null,
          sessionId: null // 清除会话ID
        };
      }
      
      // 其他普通错误，只添加事件
      return {
        events: [...state.events, { ...event, timestamp: Date.now() }]
      };
    }
    
    // 默认只添加事件
    return {
      events: [...state.events, { ...event, timestamp: Date.now() }]
    };
  }),
  
  setFinalReport: (report: string) => set({ finalReport: report }),
  
  eventSource: null,
  
  closeEventSource: () => {
    const eventSource = get().eventSource;
    if (eventSource) {
      // 关闭连接前手动触发close事件，确保清理超时检查器
      const closeEvent = new Event('close');
      eventSource.dispatchEvent(closeEvent);
      
      // 关闭连接
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
  
  // 超时检查相关变量
  let lastEventTime = Date.now();
  const TIMEOUT_DURATION = 100 * 1000; // 100秒超时
  let timeoutCheckerId: NodeJS.Timeout;
  
  // 定义更新最后事件时间的函数
  const updateLastEventTime = () => {
    lastEventTime = Date.now();
  };
  
  // 定义检查超时的函数
  const checkForTimeout = () => {
    const currentTime = Date.now();
    const timeSinceLastEvent = currentTime - lastEventTime;
    
    // 检查是否已超时
    if (timeSinceLastEvent > TIMEOUT_DURATION) {
      console.log(`Timeout detected: No events for ${timeSinceLastEvent/1000} seconds`);
      
      // 清除超时检查器
      clearInterval(timeoutCheckerId);
      
      // 关闭 EventSource 连接
      eventSource.close();
      
      // 发送超时错误事件
      addEvent({
        event: 'error',
        data: { message: `请求超时: ${TIMEOUT_DURATION/1000}秒内没有收到新的事件` }
      });
      
      // 发送中断事件
      setTimeout(() => {
        addEvent({
          event: 'task_interrupted',
          data: { message: `由于请求超时，任务已被中断` }
        });
      }, 100);
      
      // 中断后端 agent
      const store = useAgentStore.getState();
      if (store.sessionId) {
        fetch(`${API_BASE_URL}/agents/${store.sessionId}/interrupt`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        }).catch(err => {
          console.error('Failed to interrupt agent after timeout:', err);
        });
      }
      
      // 更新状态
      useAgentStore.setState({
        status: 'interrupted', 
        eventSource: null,
        sessionId: null
      });
    }
  };
  
  // 启动超时检查器 - 每10秒检查一次
  timeoutCheckerId = setInterval(checkForTimeout, 10000);
  
  eventSource.addEventListener('heartbeat', () => {
    // Keep connection alive
    updateLastEventTime();
  });
  
  // 为所有事件类型添加时间更新逻辑
  const setupEventTypeListener = (eventType: string) => {
    eventSource.addEventListener(eventType, (event) => {
      // 更新最后事件时间
      updateLastEventTime();
      
      // 之前的事件处理逻辑
      try {
        const data = JSON.parse(event.data);
        addEvent({ event: eventType as EventType, data });
        
        // 处理报告类型的特殊事件
        if (eventType === 'write_fact_checking_report_end' && data.report) {
          setFinalReport(data.report);
        }
      } catch(e) {
        console.error(`Error handling ${eventType} event:`, e);
      }
    });
  };
  
  // 为所有主要事件类型设置监听器
  [
    'extract_check_point_start', 'extract_check_point_end',
    'extract_basic_metadata_start', 'extract_basic_metadata_end',
    'extract_knowledge_start', 'extract_knowledge_end',
    'retrieve_knowledge_start', 'retrieve_knowledge_end',
    'search_agent_start', 'evaluate_status_start', 'status_evaluation_end',
    'tool_start', 'tool_result',
    'generate_answer_start', 'generate_answer_end',
    'evaluate_search_result_start', 'evaluate_search_result_end',
    'write_fact_checking_report_start', 'write_fact_checking_report_end',
    'llm_decision', 'task_complete', 'task_interrupted'
  ].forEach(setupEventTypeListener);
  
  // 特殊处理 task_complete 和 task_interrupted 事件
  eventSource.addEventListener('task_complete', (event) => {
    updateLastEventTime();
    
    const data = JSON.parse(event.data);
    addEvent({ event: 'task_complete', data });
    
    // 任务完成时清除超时检查器
    clearInterval(timeoutCheckerId);
    
    // 关闭 EventSource 连接
    if (data && data.message === "核查任务完成") {
      setTimeout(() => {
        useAgentStore.getState().closeEventSource();
      }, 500);
    }
  });
  
  eventSource.addEventListener('task_interrupted', (event) => {
    updateLastEventTime();
    
    const data = JSON.parse(event.data);
    addEvent({ event: 'task_interrupted', data });
    
    // 任务中断时清除超时检查器
    clearInterval(timeoutCheckerId);
    
    // 关闭 EventSource 连接
    setTimeout(() => {
      useAgentStore.getState().closeEventSource();
    }, 500);
  });
  
  // Error event
  eventSource.addEventListener('error', (event: MessageEvent) => {
    // 错误事件也更新最后事件时间
    updateLastEventTime();
    
    if (event.data) {
      try {
        const data = JSON.parse(event.data);
        addEvent({ event: 'error', data });
        
        // 检查是否是模型错误，如果是则关闭连接
        const errorMessage = data.message || '';
        if (
          errorMessage.includes('OpenAI API') || 
          errorMessage.includes('模型API错误') || 
          errorMessage.includes('配额') || 
          errorMessage.includes('速率限制')
        ) {
          console.log('Model API error in SSE, closing connection');
          // 清除超时检查器
          clearInterval(timeoutCheckerId);
          
          eventSource.close();
          
          // 在错误事件之后添加中断事件，确保UI状态正确更新
          setTimeout(() => {
            addEvent({ 
              event: 'task_interrupted', 
              data: { message: '由于模型API错误，任务已被中断' } 
            });
          }, 100);
        }
      } catch (e) {
        addEvent({
          event: 'error',
          data: { message: 'SSE 解析错误: ' + (event.data || '未知错误') }
        });
      }
    } else {
      // EventSource连接错误，可能是网络问题或服务器关闭了连接
      console.error('SSE connection error without data');
      
      // 清除超时检查器
      clearInterval(timeoutCheckerId);
      
      // 如果连接错误，确保前端状态正确更新
      const currentStatus = useAgentStore.getState().status;
      if (currentStatus === 'running') {
        addEvent({
          event: 'error',
          data: { message: 'SSE 连接错误，任务可能已被终止' }
        });
        
        // 添加中断事件以更新UI状态
        setTimeout(() => {
          addEvent({ 
            event: 'task_interrupted', 
            data: { message: '连接中断，任务已终止' } 
          });
        }, 100);
      } else {
        addEvent({
          event: 'error',
          data: { message: 'SSE 连接错误' }
        });
      }
    }
  });
  
  // 当EventSource关闭时清除超时检查器
  eventSource.addEventListener('close', () => {
    clearInterval(timeoutCheckerId);
  });
  
  return eventSource;
} 
export const API_BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

export interface ModelOption {
  id: string;
  name: string;
  provider: string;
  modelType: "reasoning" | "non_reasoning" | "light";
}
export const AVAILABLE_MODELS: ModelOption[] = [
  // OpenAI
  {
    id: 'chatgpt-4o-latest', 
    name: 'GPT-4o Latest', 
    provider: 'openai', 
    modelType: "non_reasoning" 
  },
  { 
    id: 'gpt-4o', 
    name: 'GPT-4o', 
    provider: 'openai', 
    modelType: "non_reasoning" 
  },
  { 
    id: 'gpt-4o-mini', 
    name: 'GPT-4o Mini', 
    provider: 'openai', 
    modelType: "light" 
  },

  // Qwen
  { 
    id: 'qwq-plus-latest', 
    name: 'QWQ 32B', 
    provider: 'qwen', 
    modelType: "reasoning" 
  },
  { 
    id: 'qwen-plus-latest', 
    name: 'Qwen Plus', 
    provider: 'qwen', 
    modelType: "non_reasoning" 
  },
  { 
    id: 'qwen-turbo', 
    name: 'Qwen Turbo', 
    provider: 'qwen', 
    modelType: "light" 
  },

  // DeepSeek
  { 
    id: 'deepseek-reasoner', 
    name: 'DeepSeek R1', 
    provider: 'deepseek', 
    modelType: "reasoning"
  },
  { 
    id: 'deepseek-chat', 
    name: 'DeepSeek V3', 
    provider: 'deepseek', 
    modelType: "non_reasoning" 
  },
];

export interface AgentBaseConfig {
  modelName: string;
  modelProvider: string;
  temperature?: number;
}

export interface MainAgentConfig extends AgentBaseConfig {
  maxRetries: number
}
export const DEFAULT_MAIN_AGENT_CONFIG: MainAgentConfig = {
  modelName: 'qwq-plus-latest',
  modelProvider: 'qwen',
  maxRetries: 3
};

export interface MetadataExtractorConfig extends AgentBaseConfig {}
export const DEFAULT_METADATA_EXTRACTOR_CONFIG: MetadataExtractorConfig = {
  modelName: 'qwen-turbo',
  modelProvider: 'qwen'
};

export interface SearchAgentConfig extends AgentBaseConfig {
  maxSearchTokens: number
  selectedTools: string[]
}
export const DEFAULT_SEARCHER_CONFIG: SearchAgentConfig = {
  modelName: 'qwen-plus-latest',
  modelProvider: 'qwen',
  maxSearchTokens: 12000,
  selectedTools: []
}; 
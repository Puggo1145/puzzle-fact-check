import { TelescopeIcon, ZapIcon, ScaleIcon, GaugeIcon } from 'lucide-react';

export const API_BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

export interface ModelOption {
  id: string;
  model: string;
  alias: string;
  provider: string;
  modelType: "reasoning" | "non_reasoning" | "light";
}
export const AVAILABLE_MODELS: ModelOption[] = [
  // OpenAI
  {
    id: 'gpt-5', 
    model: 'gpt-5', 
    alias: 'GPT 5', 
    provider: 'openai', 
    modelType: "non_reasoning" 
  },
  { 
    id: 'gpt-4.1', 
    model: 'gpt-4.1', 
    alias: 'GPT 4.1', 
    provider: 'openai', 
    modelType: "non_reasoning" 
  },
  {
    id: 'o4-mini', 
    model: 'o4-mini', 
    alias: 'O4 Mini', 
    provider: 'openai', 
    modelType: "reasoning" 
  },
  { 
    id: 'gpt-5-mini', 
    model: 'gpt-5-mini', 
    alias: 'GPT-5 Mini', 
    provider: 'openai', 
    modelType: "light" 
  },
  { 
    id: 'gpt-4.1-mini', 
    model: 'gpt-4.1-mini', 
    alias: 'GPT-4.1 Mini', 
    provider: 'openai', 
    modelType: "light" 
  },

  // Qwen
  { 
    id: 'qwen-flash', 
    model: 'qwen-flash', 
    alias: 'Qwen Flash', 
    provider: 'qwen', 
    modelType: "reasoning" 
  },
  { 
    id: 'qwq-plus-latest', 
    model: 'qwq-plus-latest', 
    alias: 'qwq 32B', 
    provider: 'qwen', 
    modelType: "reasoning" 
  },
  { 
    id: 'qwen-plus-latest', 
    model: 'qwen-plus-latest', 
    alias: 'Qwen Plus', 
    provider: 'qwen', 
    modelType: "non_reasoning" 
  },
  { 
    id: 'qwen-max-latest', 
    model: 'qwen-max-latest', 
    alias: 'Qwen Max', 
    provider: 'qwen', 
    modelType: "non_reasoning" 
  },
  { 
    id: 'qwen-turbo-latest', 
    model: 'qwen-turbo-latest', 
    alias: 'Qwen Turbo', 
    provider: 'qwen', 
    modelType: "light" 
  },

  // DeepSeek
  { 
    id: 'deepseek-reasoner', 
    model: 'deepseek-reasoner', 
    alias: 'DeepSeek R1', 
    provider: 'deepseek', 
    modelType: "reasoning"
  },
  { 
    id: 'deepseek-chat', 
    model: 'deepseek-chat', 
    alias: 'DeepSeek V3', 
    provider: 'deepseek', 
    modelType: "non_reasoning" 
  },

  // // OpenAI Third Party
  // {
  //   id: 'gpt-4o-mini-third-party',
  //   model: 'gpt-4o-mini',
  //   alias: 'GPT-4o Mini',
  //   provider: 'openai_third_party',
  //   modelType: "light"
  // },
  // {
  //   id: 'gpt-4o-third-party',
  //   model: 'gpt-4o',
  //   alias: 'GPT-4o',
  //   provider: 'openai_third_party',
  //   modelType: "non_reasoning"
  // },
  // {
  //   id: 'chatgpt-4o-latest-third-party',
  //   model: 'chatgpt-4o-latest',
  //   alias: 'ChatGPT-4o Latest',
  //   provider: 'openai_third_party',
  //   modelType: "non_reasoning"
  // },
];

export interface AgentBaseConfig {
  modelId: string;
  modelName: string;
  modelProvider: string;
  temperature?: number;
}

export interface MainAgentConfig extends AgentBaseConfig {
  maxRetries: number
}
export const MAIN_AGENT_MODELS = AVAILABLE_MODELS.filter((model) => model.modelType !== "light")

export interface MetadataExtractorConfig extends AgentBaseConfig {}
export const METADATA_EXTRACTOR_MODELS = AVAILABLE_MODELS

export interface SearchAgentConfig extends AgentBaseConfig {
  maxSearchTokens: number
  selectedTools: string[]
}
export const SEARCH_AGENT_MODELS = AVAILABLE_MODELS.filter((model) => model.modelType !== "light")

// 预设配置
export interface ConfigPreset {
  id: string;
  name: string;
  description: string;
  icon: React.FC<React.SVGProps<SVGSVGElement>>;
  mainConfig: MainAgentConfig;
  metadataConfig: MetadataExtractorConfig;
  searchConfig: SearchAgentConfig;
}
export const CONFIG_PRESETS: ConfigPreset[] = [
  {
    id: 'lightweight',
    name: 'fast',
    description: 'good for simple news. Fastest speed.',
    icon: GaugeIcon,
    mainConfig: {
      modelId: 'qwen-plus-latest',
      modelName: 'qwen-plus-latest',
      modelProvider: 'qwen',
      maxRetries: 1
    },
    metadataConfig: {
      modelId: 'qwen-turbo-latest',
      modelName: 'qwen-turbo-latest',
      modelProvider: 'qwen'
    },
    searchConfig: {
      modelId: 'qwen-plus-latest',
      modelName: 'qwen-plus-latest',
      modelProvider: 'qwen',
      maxSearchTokens: 10000,
      selectedTools: []
    }
  },
  {
    id: 'standard',
    name: 'balanced',
    description: 'Good for most news. Balanced speed.',
    icon: ScaleIcon,
    mainConfig: {
      modelId: 'qwen-max-latest',
      modelName: 'qwen-max-latest',
      modelProvider: 'qwen',
      maxRetries: 2
    },
    metadataConfig: {
      modelId: 'qwen-turbo-latest',
      modelName: 'qwen-turbo-latest',
      modelProvider: 'qwen'
    },
    searchConfig: {
      modelId: 'qwen-plus-latest',
      modelName: 'qwen-plus-latest',
      modelProvider: 'qwen',
      maxSearchTokens: 20000,
      selectedTools: []
    }
  },
  {
    id: 'high-performance',
    name: 'high-performance',
    description: 'Good for complex news. Takes longer time.',
    icon: ZapIcon,
    mainConfig: {
      modelId: 'qwen-max-latest',
      modelName: 'qwen-max-latest',
      modelProvider: 'qwen',
      maxRetries: 3
    },
    metadataConfig: {
      modelId: 'qwen-plus-latest',
      modelName: 'qwen-plus-latest',
      modelProvider: 'qwen'
    },
    searchConfig: {
      modelId: 'qwen-max-latest',
      modelName: 'qwen-max-latest',
      modelProvider: 'qwen',
      maxSearchTokens: 30000,
      selectedTools: []
    }
  },
  {
    id: 'deep-check-max',
    name: 'deep-check-max',
    description: 'Use stronger model and larger context. Takes longer time. Most expensive.',
    icon: TelescopeIcon,
    mainConfig: {
      modelId: 'gpt-5',
      modelName: 'gpt-5',
      modelProvider: 'openai',
      maxRetries: 3
    },
    metadataConfig: {
      modelId: 'gpt-5-mini',
      modelName: 'gpt-5-mini',
      modelProvider: 'openai'
    },
    searchConfig: {
      modelId: 'gpt-5',
      modelName: 'gpt-5',
      modelProvider: 'openai',
      maxSearchTokens: 50000,
      selectedTools: []
    }
  },
];
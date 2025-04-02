import { ZapIcon, ScaleIcon, FeatherIcon } from 'lucide-react';

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
    id: 'gpt-4o', 
    model: 'gpt-4o', 
    alias: 'GPT-4o', 
    provider: 'openai', 
    modelType: "non_reasoning" 
  },
  {
    id: 'chatgpt-4o-latest', 
    model: 'chatgpt-4o-latest', 
    alias: 'ChatGPT-4o Latest', 
    provider: 'openai', 
    modelType: "non_reasoning" 
  },
  // TODO： 添加 O3 Mini 模型
  // { 
  //   id: 'o3-mini', 
  //   model: 'o3-mini', 
  //   alias: 'O3 Mini', 
  //   provider: 'openai', 
  //   modelType: "reasoning" 
  // },
  { 
    id: 'gpt-4o-mini', 
    model: 'gpt-4o-mini', 
    alias: 'GPT-4o Mini', 
    provider: 'openai', 
    modelType: "light" 
  },

  // Qwen
  { 
    id: 'qwq-plus-latest', 
    model: 'qwq-plus-latest', 
    alias: 'QWQ 32B', 
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
    id: 'qwen-turbo', 
    model: 'qwen-turbo', 
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

  // OpenAI Third Party
  {
    id: 'gpt-4o-mini-third-party',
    model: 'gpt-4o-mini',
    alias: 'GPT-4o Mini',
    provider: 'openai_third_party',
    modelType: "light"
  },
  {
    id: 'gpt-4o-third-party',
    model: 'gpt-4o',
    alias: 'GPT-4o',
    provider: 'openai_third_party',
    modelType: "non_reasoning"
  },
  {
    id: 'chatgpt-4o-latest-third-party',
    model: 'chatgpt-4o-latest',
    alias: 'ChatGPT-4o Latest',
    provider: 'openai_third_party',
    modelType: "non_reasoning"
  },
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
export const DEFAULT_MAIN_AGENT_CONFIG: MainAgentConfig = {
  modelId: 'qwq-plus-latest',
  modelName: 'qwq-plus-latest',
  modelProvider: 'qwen',
  maxRetries: 2
};
export const MAIN_AGENT_EXCLUDED_MODELS = ['gpt-4o-mini', 'qwen-turbo'];

export interface MetadataExtractorConfig extends AgentBaseConfig {}
export const DEFAULT_METADATA_EXTRACTOR_CONFIG: MetadataExtractorConfig = {
  modelId: 'qwen-turbo',
  modelName: 'qwen-turbo',
  modelProvider: 'qwen'
};

export interface SearchAgentConfig extends AgentBaseConfig {
  maxSearchTokens: number
  selectedTools: string[]
}
export const DEFAULT_SEARCHER_CONFIG: SearchAgentConfig = {
  modelId: 'qwen-plus-latest',
  modelName: 'qwen-plus-latest',
  modelProvider: 'qwen',
  maxSearchTokens: 12000,
  selectedTools: []
}; 
export const SEARCHER_EXCLUDED_MODELS = ['gpt-4o-mini', 'qwen-turbo'];

// 预设配置
export interface ConfigPreset {
  id: string;
  name: string;
  description: string;
  icon: React.FC<React.SVGProps<SVGSVGElement>>;
  mainConfig: Partial<MainAgentConfig>;
  metadataConfig: Partial<MetadataExtractorConfig>;
  searchConfig: Partial<SearchAgentConfig>;
}
export const CONFIG_PRESETS: ConfigPreset[] = [
  {
    id: 'high-performance',
    name: '高性能模式',
    description: '适合对复杂新闻进行事实核查，速度最慢',
    icon: ZapIcon,
    mainConfig: {
      modelId: 'qwq-plus-latest',
      modelName: 'qwq-plus-latest',
      modelProvider: 'qwen',
      maxRetries: 3
    },
    metadataConfig: {
      modelId: 'qwen-plus-latest',
      modelName: 'qwen-plus-latest',
      modelProvider: 'qwen'
    },
    searchConfig: {
      modelId: 'qwq-plus-latest',
      modelName: 'qwq-plus-latest',
      modelProvider: 'qwen',
      maxSearchTokens: 15000
    }
  },
  {
    id: 'standard',
    name: '均衡模式',
    description: '适合对大部分新闻进行事实核查，速度较快',
    icon: ScaleIcon,
    mainConfig: {
      modelId: 'qwq-plus-latest',
      modelName: 'qwq-plus-latest',
      modelProvider: 'qwen',
      maxRetries: 2
    },
    metadataConfig: {
      modelId: 'qwen-turbo',
      modelName: 'qwen-turbo',
      modelProvider: 'qwen'
    },
    searchConfig: {
      modelId: 'qwen-plus-latest',
      modelName: 'qwen-plus-latest',
      modelProvider: 'qwen',
      maxSearchTokens: 10000
    }
  },
  {
    id: 'lightweight',
    name: '快速模式',
    description: '适合对简单新闻进行事实核查，速度最快',
    icon: FeatherIcon,
    mainConfig: {
      modelId: 'qwen-plus-latest',
      modelName: 'qwen-plus-latest',
      modelProvider: 'qwen',
      maxRetries: 1
    },
    metadataConfig: {
      modelId: 'qwen-turbo',
      modelName: 'qwen-turbo',
      modelProvider: 'qwen'
    },
    searchConfig: {
      modelId: 'qwen-plus-latest',
      modelName: 'qwen-plus-latest',
      modelProvider: 'qwen',
      maxSearchTokens: 7000
    }
  }
];
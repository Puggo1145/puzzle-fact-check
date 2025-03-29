import { 
  MainAgentConfig,
  MetadataExtractorConfig,
  ModelOption,
  SearchAgentConfig
} from "@/constants/agent-default-config";
import type { Event, EventType, TypedEvent } from "@/types/events";

export type AgentStatus =
  | 'idle'
  | 'running'
  | 'interrupting'
  | 'interrupted'
  | 'completed';

export interface AgentState {
  sessionId: string | null;
  status: AgentStatus;
  events: Event<any>[];
  finalReport: string;
  newsText: string;
  // Agent configurations
  mainAgentConfig: MainAgentConfig;
  metadataExtractorConfig: MetadataExtractorConfig;
  searcherConfig: SearchAgentConfig;
  // Available models
  availableModels: ModelOption[];
  // EventSource
  eventSource: EventSource | null;
  // Selected tools
  selectedTools: string[];
  // Actions
  setNewsText: (text: string) => void;
  setMainAgentConfig: (config: Partial<MainAgentConfig>) => void;
  setMetadataExtractorConfig: (config: Partial<MetadataExtractorConfig>) => void;
  setSearcherConfig: (config: Partial<SearchAgentConfig>) => void;
  setSelectedTools: (tools: string[]) => void;
  interruptAgent: () => Promise<void>;
  resetState: () => void;
  addEvent: <T extends EventType>(event: TypedEvent<T>) => void;
  setFinalReport: (report: string) => void;
  closeEventSource: () => void;
  createAndRunAgent: () => Promise<void>;
} 
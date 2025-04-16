import { 
  MainAgentConfig,
  MetadataExtractorConfig,
  ModelOption,
  SearchAgentConfig
} from "@/constants/agent-default-config";
import type { Event, EventType } from "@/types/events";

export type AgentStatus =
  | 'idle'
  | 'running'
  | 'interrupting'
  | 'interrupted'
  | 'completed';

export type Verdict = "true" | "mostly-true" | "mostly-false" | "false" | "no-enough-evidence";

export interface AgentState {
  sessionId: string | null;
  status: AgentStatus;
  events: Event<any>[];
  result: {
    report?: string;
    verdict?: Verdict;
  };
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
  addEvent: (event: Event) => void;
  setResult: (report: string, verdict: Verdict) => void;
  closeEventSource: () => void;
  createAndRunAgent: () => Promise<void>;
} 
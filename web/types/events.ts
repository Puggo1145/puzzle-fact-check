export type EventType =
    | 'agent_start'
    | 'check_if_news_text_start'
    | 'check_if_news_text_end'
    | 'extract_basic_metadata_start'
    | 'extract_basic_metadata_end'
    | 'extract_knowledge_start'
    | 'extract_knowledge_end'
    | 'retrieve_knowledge_start'
    | 'retrieve_knowledge_end'
    | 'extract_check_point_start'
    | 'extract_check_point_end'
    | 'search_agent_start'
    | 'evaluate_current_status_start'
    | 'evaluate_current_status_end'
    | 'generate_answer_start'
    | 'generate_answer_end'
    | 'evaluate_search_result_start'
    | 'evaluate_search_result_end'
    | 'llm_decision'
    | 'write_fact_check_report_start'
    | 'write_fact_check_report_end'
    | 'tool_start'
    | 'tool_end'
    | 'task_complete'
    | 'task_interrupted'
    | 'error'
    | 'stream_closed';

export interface Event<T=any> {
    event: EventType;
    data?: T;
}

// IsNewsText interface
export interface IsNewsText {
    result: boolean;
    reason: string;
}

// Main Agent Events
export interface RetrievalStep {
    id: string;
    purpose: string;
    expected_sources: string[];
    result?: RetrievalResult;
    verification?: RetrievalResultVerification;
}

export interface CheckPoint {
    id: string;
    content: string;
    is_verification_point: boolean;
    importance?: string;
    retrieval_step?: RetrievalStep[];
}

// Metadata Extractor Events
export interface BasicMetadata {
    news_type: string;
    who?: string[];
    when?: string[];
    where?: string[];
    what?: string[];
    why?: string[];
    how?: string[];
}
export interface Knowledge {
    term: string;
    category: string;
    description?: string;
    source?: string;
}

// Search Agent Events
export interface SearchAgentStartData {
    content: string;
    purpose: string;
    expected_sources: string[];
}

export interface Status {
    evaluation: string;
    missing_information: string;
    new_evidence: Evidence[];
    memory: string;
    next_step: string;
}

export interface Evidence {
    content: string;
    source: Record<string, string>;
    reasoning: string;
    relationship: "support" | "contradict";
}

export interface SearchResult {
    summary: string;
    conclusion: string;
    confidence: string;
}
export interface RetrievalResult extends SearchResult {
    check_point_id: string;
    retrieval_step_id: string;
    evidences: Evidence[];
}
export interface RetrievalResultVerification {
    reasoning: string;
    verified?: boolean;
    updated_purpose?: string;
    updated_expected_sources?: string[];
}

export interface ToolStartData {
    tool_name: string;
    input_str: string;
}

export interface ToolEndData {
    tool_name: string;
    output_str: string;
}

export interface LLMDecisionData {
    decision: string;
    reason: string | null;
}

export interface FactCheckReportData {
    report: string;
}

export interface TaskCompleteData {
    message: string;
    result: any; // This could be further typed if the structure is consistent
}

export interface TaskInterruptedData {
    message: string;
}

export interface ErrorData {
    message: string;
}

// Map each event type to its corresponding data interface
export type EventDataMap = {
    'agent_start': undefined;
    'check_if_news_text_start': undefined;
    'check_if_news_text_end': IsNewsText;
    'extract_check_point_start': undefined;
    'extract_check_point_end': CheckPoint[];
    'extract_basic_metadata_start': undefined;
    'extract_basic_metadata_end': BasicMetadata;
    'extract_knowledge_start': undefined;
    'extract_knowledge_end': Knowledge[];
    'retrieve_knowledge_start': undefined;
    'retrieve_knowledge_end': Knowledge;
    'search_agent_start': SearchAgentStartData;
    'evaluate_current_status_start': undefined;
    'evaluate_current_status_end': Status;
    'tool_start': ToolStartData;
    'tool_end': ToolEndData;
    'generate_answer_start': undefined;
    'generate_answer_end': SearchResult;
    'evaluate_search_result_start': undefined;
    'evaluate_search_result_end': RetrievalResultVerification;
    'write_fact_check_report_start': undefined;
    'write_fact_check_report_end': FactCheckReportData;
    'llm_decision': LLMDecisionData;
    'task_complete': TaskCompleteData;
    'task_interrupted': TaskInterruptedData;
    'error': ErrorData;
    'stream_closed': {};
}

// Type-safe event helper
export type TypedEvent<T extends EventType> = Event<EventDataMap[T]>;

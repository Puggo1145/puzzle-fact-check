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
export const eventTypes: EventType[] = [
    'agent_start',
    'check_if_news_text_start', 'check_if_news_text_end',
    'extract_check_point_start', 'extract_check_point_end',
    'extract_basic_metadata_start', 'extract_basic_metadata_end',
    'extract_knowledge_start', 'extract_knowledge_end',
    'retrieve_knowledge_start', 'retrieve_knowledge_end',
    'search_agent_start', 'evaluate_current_status_start', 'evaluate_current_status_end',
    'tool_start', 'tool_end',
    'generate_answer_start', 'generate_answer_end',
    'evaluate_search_result_start', 'evaluate_search_result_end',
    'write_fact_check_report_start', 'write_fact_check_report_end',
    'llm_decision', 'task_complete', 'task_interrupted',
    'error',
];


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
    expected_source: string;
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
    expected_source: string;
}

export interface Status {
    evaluation: string;
    missing_information: string;
    new_evidence: Evidence[];
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
    updated_expected_source?: string;
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

export interface FactCheckResultData {
    report: string;
    verdict: "true" | "mostly-true" | "mostly-false" | "false" | "no-enough-evidence";
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

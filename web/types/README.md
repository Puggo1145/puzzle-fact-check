# Event Type System

This document explains the event type system used for handling Server-Sent Events (SSE) in the Puzzle Fact Checker application.

## Overview

The application uses a strongly typed event system to handle all events flowing from the backend to the frontend. This ensures type safety throughout the application and provides better development experience with autocompletion.

## Key Components

### 1. Event Types (`events.ts`)

- `EventType`: A union type of all possible event names that can be sent by the backend.
- `Event<T>`: A generic interface for any event, containing an event type and optional data payload.
- `TypedEvent<T extends EventType>`: A helper type that maps each event type to its corresponding data interface.
- `EventDataMap`: A mapping from event types to their respective data interface types.

### 2. Event Name Prefixes

The backend sends events with two different naming patterns:
- Events with a `print_` prefix (e.g., `print_extract_basic_metadata_start`)
- Events without the prefix (e.g., `extract_basic_metadata_start`)

Our type system and event handling support both formats. When processing events, we normalize event names by removing the `print_` prefix if present.

### 3. Special Events

- `agent_start`: Signals the start of the agent's task
- `task_complete`: Signals successful completion
- `task_interrupted`: Signals that the task was interrupted
- `error`: Indicates an error occurred

### 4. Data Interfaces

For each event type, there's a corresponding interface that defines the structure of its data payload:

- `CheckPointEndData`: Data for extracted verification points
- `BasicMetadataEndData`: Data for basic metadata extraction
- `KnowledgeEndData`: Data for knowledge extraction
- `RetrieveKnowledgeEndData`: Data for knowledge retrieval
- `SearchAgentStartData`: Data for search agent initialization
- `StatusEvaluationEndData`: Data for search status evaluation
- `ToolStartData`: Data for tool execution
- `ToolResultData`: Data for tool execution results
- `GenerateAnswerEndData`: Data for answer generation
- `EvaluateSearchResultEndData`: Data for search result verification
- `WriteReportEndData`: Data for fact-checking report
- `LLMDecisionData`: Data for LLM decision events
- `TaskCompleteData`: Data for task completion
- `TaskInterruptedData`: Data for task interruption
- `ErrorData`: Data for error events

### 5. Model Interfaces

Base models that match the Python Pydantic models in the backend:

- `CheckPoint`: A verification point with fields matching the Pydantic model (id, content, is_verification_point, importance, retrieval_step)
- `CheckPoints`: Collection of verification points
- `RetrievalStep`: A search step with fields matching the Pydantic model (id, purpose, expected_sources, result, verification)
- `RetrievalResult`: Extends SearchResult with additional fields (check_point_id, retrieval_step_id, evidences)
- `RetrievalResultVerification`: Verification result with fields (reasoning, verified, updated_purpose, updated_expected_sources)
- `Knowledge`: A knowledge element with fields (term, category, description, source)
- `Knowledges`: Collection of knowledge elements
- `BasicMetadata`: Metadata about the news article with 5W1H fields (news_type, who, when, where, what, why, how)
- `Evidence`: Supporting evidence with fields (content, source, reasoning, relationship)
- `SearchResult`: Result of a search operation (summary, conclusion, confidence)

## Backend to Frontend Data Flow

The backend sends data as JSON strings that need to be parsed in the frontend:

1. Pydantic models in Python are serialized to JSON using `model_dump_json()`
2. These are sent as SSE events with their corresponding event type (with or without `print_` prefix)
3. In the frontend, we need to:
   - Correctly type the event data based on the event type
   - Normalize the event type by removing the `print_` prefix if present
   - Parse the JSON strings back into their corresponding TypeScript interfaces

For example, for `extract_check_point_end` events:
```typescript
// Backend sends:
{
  "event": "print_extract_check_point_end",
  "data": {
    "check_points": "{ \"items\": [ ... JSON string of CheckPoints ... ] }"
  }
}

// In frontend:
const normalizedEventType = eventType.startsWith('print_') ? eventType.substring(6) : eventType;
if (normalizedEventType === 'extract_check_point_end') {
  const typedData = data as CheckPointEndData;
  const parsedCheckPoints: CheckPoints = JSON.parse(typedData.check_points);
}
```

## Usage

```typescript
// Creating a typed event
const event: TypedEvent<'task_complete'> = {
  event: 'task_complete',
  data: {
    message: '核查任务完成',
    result: {...}
  }
};

// Access data with proper typing
if (event.event === 'task_complete') {
  console.log(event.data.message); // TypeScript knows data has message property
}

// Handling events with print_ prefix normalization
const handleEvent = <T extends EventType>(event: TypedEvent<T>) => {
  // Normalize event type by removing print_ prefix if present
  const normalizedEventType = event.event.startsWith('print_') 
    ? event.event.substring(6) 
    : event.event;

  switch(normalizedEventType) {
    case 'extract_check_point_end':
      // TypeScript knows event.data is CheckPointEndData
      const checkPointData = JSON.parse(event.data.check_points);
      break;
    case 'error':
      // TypeScript knows event.data is ErrorData
      console.error(event.data.message);
      break;
  }
};
```

## Event Flow

1. Backend sends SSE events with specific event types (with or without `print_` prefix) and data payloads.
2. The `setupEventSource` function in `eventHandler.ts` listens for these events.
3. Events are normalized, parsed, and typed according to their event type.
4. The `addEvent` function in the agent store adds these events to the state.
6. The `EventLog` component in the UI displays the filtered events.
7. `EventItem` component renders each event according to its normalized type and data.

## Notes

- Some event data comes as JSON strings that need to be parsed in the UI before use.
- The backend uses Pydantic models which are serialized to JSON strings before sending. 
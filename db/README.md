# Database Integration for Agent System

This document explains how to integrate the agent system with the Neo4j database.

## Architecture

The database integration follows a layered architecture to ensure separation of concerns and maintainability:

1. **Schema Layer** (`db/schema.py`): Defines the database schema using neomodel.
2. **Service Layer** (`db/services.py`): Provides low-level database operations.
3. **Repository Layer** (`db/repository.py`): Provides higher-level operations for specific entities.
4. **Integration Layer** (`db/integrations.py`): Connects agents with database operations.

## Integration with Agents

The integration with agents is designed to be loosely coupled. Each agent can optionally receive a database integration instance, which it can use to store its state in the database.

### Main Agent

The Main Agent is responsible for orchestrating the entire fact-checking process. It initializes the database integration with the news text and passes it to the child agents.

```python
# Example usage
from db.integrations import AgentDatabaseIntegration

# Create database integration
db_integration = AgentDatabaseIntegration()

# Create main agent with database integration
main_agent = MainAgent(
    model=model,
    metadata_extract_model=metadata_model,
    search_model=search_model,
    db_integration=db_integration
)

# Invoke main agent
result = main_agent.invoke({"news_text": news_text})
```

### Metadata Extract Agent

The Metadata Extract Agent extracts metadata from the news text and stores it in the database.

```python
# Example usage
metadata_agent = MetadataExtractAgentGraph(
    model=metadata_model,
    db_integration=db_integration
)
```

### Search Agent

The Search Agent performs searches and stores the results in the database.

```python
# Example usage
search_agent = SearchAgentGraphWithDB(
    model=search_model,
    max_tokens=12000,
    db_integration=db_integration
)
```

## Database Schema

The database schema is designed to represent the fact-checking process:

- `NewsText`: Represents the news text being fact-checked.
- `BasicMetadata`: Represents the basic metadata of the news text.
- `Knowledge`: Represents knowledge elements extracted from the news text.
- `CheckPoint`: Represents fact-checking points extracted from the news text.
- `RetrievalStep`: Represents steps to retrieve information for fact-checking.
- `SearchResult`: Represents the results of a search.
- `Evidence`: Represents evidence supporting or contradicting a fact-checking point.

## Relationships

The relationships between entities are as follows:

- `NewsText` <-[:HAS_BASIC_METADATA]- `BasicMetadata`
- `NewsText` <-[:HAS_KNOWLEDGE]- `Knowledge`
- `NewsText` <-[:CHECKED_BY]- `CheckPoint`
- `CheckPoint` <-[:VERIFIED_BY]- `RetrievalStep`
- `RetrievalStep` <-[:HAS_RESULT]- `SearchResult`
- `RetrievalStep` <-[:SUPPORTS_BY]- `Evidence`
- `RetrievalStep` <-[:CONTRADICTS_WITH]- `Evidence`

## Usage

To use the database integration, follow these steps:

1. Initialize the database integration with the news text:
   ```python
   db_integration = AgentDatabaseIntegration()
   db_integration.initialize_with_news_text(news_text)
   ```

2. Store metadata:
   ```python
   db_integration.store_metadata_state(metadata_state)
   ```

3. Store check points:
   ```python
   db_integration.store_check_points(check_points)
   ```

4. Store search results:
   ```python
   db_integration.store_search_results(search_state)
   ```

## Transactions

Database operations are wrapped in transactions to ensure data consistency. The `@DatabaseService.transaction` decorator is used to wrap methods in a transaction.

## Error Handling

The integration layer includes error handling to ensure that database operations do not fail silently. If a database operation fails, an exception is raised with a descriptive error message. 
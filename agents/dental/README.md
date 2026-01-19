# Dental Agent

A specialized LangGraph agent for answering dental clinical questions with evidence-based citations.

## Overview

The Dental Agent (Huiya/慧牙) is designed to help dental professionals find evidence-based answers to clinical questions. It uses web search (via Tavily API) to retrieve relevant dental literature and provides citations in responses.

## Features

- **Evidence-based answers**: Always searches for citations before answering clinical questions
- **Bilingual support**: Responds in the same language as the user's question (English/Chinese)
- **Citation format**: Provides inline citations [1], [2], etc. from search results
- **Clinical focus**: Specialized for dental topics

## Configuration

The agent uses the following environment variables:

- `TAVILY_API_KEY`: API key for Tavily web search (required for citation retrieval)
- `GOOGLE_API_KEY`: API key for Google Gemini models (default LLM provider)
- `ANTHROPIC_API_KEY`: Optional, for using Claude models
- `OPENAI_API_KEY`: Optional, for using OpenAI models

## Usage

### From LangGraph Platform

```bash
# Start LangGraph server
langgraph dev

# The agent will be available at:
# POST http://localhost:2024/runs/stream
```

### HTTP Request Example

```json
{
  "assistant_id": "dental_agent",
  "input": {
    "messages": [
      {
        "role": "user",
        "content": "What is the recommended amoxicillin dosage for dental infections?"
      }
    ]
  },
  "metadata": {
    "llm_provider": "gemini",
    "llm_tier": "pro",
    "enable_thinking": true
  }
}
```

### Metadata Options

- `llm_provider`: "gemini" (default), "anthropic", or "openai"
- `llm_tier`: "pro" (default) or "flash"
- `llm_model`: Specific model ID (overrides tier)
- `enable_thinking`: true (default) or false
- `thinking_budget`: Token budget for thinking (default: 2048)

## Tools

### search_dental_literature

Searches dental literature using Tavily API and returns relevant citations.

**Parameters:**
- `query` (str): The dental topic or question to search for

**Returns:**
- List of citations with:
  - `id`: Unique citation ID
  - `marker`: Display marker (e.g., "[1]")
  - `title`: Source title
  - `publication`: Journal or guideline name
  - `year`: Publication year
  - `url`: Link to source

## System Prompt

The agent uses a specialized system prompt that:
- Enforces tool usage before answering
- Requires citation formatting
- Matches user language
- Focuses on clinical, actionable responses

## Development

The agent follows the nexus-langgraph pattern:
- Factory function: `async def agent(config: RunnableConfig)`
- Uses `create_agent` from LangChain
- Leverages shared utilities from `shared.config.llm_config`
- Tools defined in `agents/dental/tools.py`

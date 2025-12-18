# Proposed Repository Structure for `nexus-langgraph`

## Overview

A repository to store various LangGraph agents based on Nexus, designed for deployment on LangGraph Platform. This structure supports multiple agents, shared utilities, and easy deployment.

## Proposed Structure

```
nexus-langgraph/
├── README.md                          # Main repository documentation
├── pyproject.toml                     # Root package configuration
├── langgraph.json                     # LangGraph Platform deployment config
├── .env.example                       # Environment variables template
├── .gitignore
├── LICENSE
│
├── agents/                            # Individual agent implementations
│   ├── __init__.py
│   ├── react/                         # General-purpose ReAct agent
│   │   ├── __init__.py
│   │   ├── agent.py                   # Main agent graph definition
│   │   ├── README.md                  # Agent-specific documentation
│   │   └── config.py                  # Agent-specific configuration
│   │
│   ├── quant/                         # Quantitative trading agent
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── README.md
│   │   ├── config.py
│   │   └── strategies/                # Strategy-specific code
│   │       └── backtest.py
│   │
│   ├── talent/                        # Talent & company search agent
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── README.md
│   │   └── config.py
│   │
│   └── code_analyzer/                 # Code analysis agent (future)
│       ├── __init__.py
│       ├── agent.py
│       └── README.md
│
├── shared/                            # Shared utilities and tools
│   ├── __init__.py
│   ├── tools/                         # Nexus tools for LangGraph
│   │   ├── __init__.py
│   │   ├── nexus_tools.py             # Core Nexus file operations
│   │   ├── e2b_tools.py               # E2B sandbox tools (optional)
│   │   └── web_tools.py               # Web scraping/search tools (optional)
│   │
│   ├── prompts/                       # Shared system prompts
│   │   ├── __init__.py
│   │   ├── react_prompt.py            # ReAct agent prompts
│   │   ├── coding_prompt.py           # Coding agent prompts
│   │   └── analysis_prompt.py        # Analysis agent prompts
│   │
│   ├── config/                        # Configuration utilities
│   │   ├── __init__.py
│   │   ├── nexus_config.py            # Nexus connection helpers
│   │   └── llm_config.py             # LLM provider configuration
│   │
│   └── utils/                         # General utilities
│       ├── __init__.py
│       ├── auth.py                    # Authentication helpers
│       └── logging.py                 # Logging configuration
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py                    # Pytest configuration
│   ├── test_agents/
│   │   ├── test_react_agent.py
│   │   ├── test_quant_agent.py
│   │   └── test_talent_agent.py
│   └── test_shared/
│       ├── test_tools.py
│       └── test_config.py
│
├── examples/                          # Example usage and demos
│   ├── basic_usage.py                 # Simple agent invocation
│   ├── multi_agent.py                 # Multi-agent collaboration
│   └── custom_tools.py                # Adding custom tools
│
├── scripts/                           # Utility scripts
│   ├── setup_test_data.py             # Populate Nexus with test data
│   ├── deploy.sh                      # Deployment helper
│   └── validate_agents.py             # Validate all agents
│
└── docs/                              # Additional documentation
    ├── deployment.md                  # LangGraph Platform deployment guide
    ├── adding_agents.md               # Guide for adding new agents
    ├── architecture.md                # System architecture
    └── best_practices.md              # Development best practices
```

## Key Design Decisions

### 1. Agent Organization (`agents/`)

Each agent is in its own directory with:
- `agent.py` - Main LangGraph graph definition (exported as `agent`)
- `README.md` - Agent-specific documentation
- `config.py` - Agent-specific configuration (optional)

**Benefits:**
- Clear separation of concerns
- Easy to add new agents
- Each agent can have its own dependencies if needed
- Self-contained and deployable

### 2. Shared Utilities (`shared/`)

Common code used across multiple agents:
- **`tools/`** - LangGraph tools (Nexus operations, E2B, web)
- **`prompts/`** - Reusable system prompts
- **`config/`** - Configuration helpers
- **`utils/`** - General utilities

**Benefits:**
- DRY principle (Don't Repeat Yourself)
- Consistent tool implementations
- Easy to update shared functionality
- Clear separation of shared vs agent-specific code

### 3. LangGraph Platform Configuration

**`langgraph.json`** at root:
```json
{
  "dependencies": ["."],
  "graphs": {
    "react": "./agents/react/agent.py:agent",
    "quant": "./agents/quant/agent.py:agent",
    "talent": "./agents/talent/agent.py:agent"
  },
  "env": ".env"
}
```

**Benefits:**
- Single deployment config
- All agents deployable from one repo
- Easy to add/remove agents
- Standard LangGraph Platform format

### 4. Root `pyproject.toml`

```toml
[project]
name = "nexus-langgraph"
version = "0.1.0"
description = "LangGraph agents with Nexus filesystem integration"
requires-python = ">=3.11"
dependencies = [
    "nexus-fs-python[langgraph]>=0.1.0",
    "langgraph>=0.2.0",
    "langchain-core>=0.3.0",
    "langchain-anthropic>=0.2.0",
    "langchain-openai>=0.2.0",
    # Optional dependencies
    "e2b-code-interpreter>=1.0.0",  # For sandbox tools
    "tavily-python>=0.3.0",         # For web search
    "firecrawl-py>=1.0.0",           # For web scraping
]
```

## Agent Structure Example

### `agents/react/agent.py`

```python
"""General-purpose ReAct agent with Nexus filesystem access."""

from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from shared.tools.nexus_tools import get_nexus_tools
from shared.prompts.react_prompt import get_system_prompt

def get_agent():
    """Create and return the ReAct agent graph."""
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
    tools = get_nexus_tools()
    
    agent = create_react_agent(
        llm,
        tools,
        state_modifier=get_system_prompt(),
    )
    
    return agent

# Export for langgraph.json
agent = get_agent()
```

### `agents/react/README.md`

```markdown
# ReAct Agent

General-purpose ReAct agent with Nexus filesystem access.

## Features
- File search and analysis
- Code reading and writing
- Documentation generation

## Usage
Deploy via LangGraph Platform as `react` assistant.
```

## Migration Plan

### Phase 1: Repository Setup
1. Create `nexus-langgraph` repository
2. Set up basic structure (directories)
3. Create root `pyproject.toml` and `langgraph.json`

### Phase 2: Move Shared Code
1. Move `nexus_tools.py` → `shared/tools/nexus_tools.py`
2. Extract prompts → `shared/prompts/`
3. Create config helpers → `shared/config/`

### Phase 3: Migrate Agents
1. Move `react_agent.py` → `agents/react/agent.py`
2. Move `quant_agent.py` → `agents/quant/agent.py`
3. Move `talent_agent.py` → `agents/talent/agent.py`
4. Update imports to use shared utilities

### Phase 4: Testing & Documentation
1. Add tests for each agent
2. Update README files
3. Create deployment documentation
4. Add examples

## Alternative Structure (Simpler)

If you prefer a flatter structure:

```
nexus-langgraph/
├── agents/
│   ├── react_agent.py
│   ├── quant_agent.py
│   └── talent_agent.py
├── tools/
│   └── nexus_tools.py
├── prompts/
│   └── system_prompts.py
└── langgraph.json
```

**Trade-offs:**
- ✅ Simpler, fewer directories
- ❌ Less scalable for many agents
- ❌ Harder to organize agent-specific code

## Recommendations

I recommend the **first structure** (with `agents/` subdirectories) because:

1. **Scalability** - Easy to add 10+ agents without clutter
2. **Organization** - Each agent can have its own config, docs, tests
3. **Deployment** - LangGraph Platform supports this structure
4. **Maintainability** - Clear separation makes updates easier
5. **Best Practices** - Follows common Python project patterns

## Questions to Consider

1. **Agent-specific dependencies?** 
   - If some agents need unique packages, we can add per-agent `pyproject.toml`
   - Or use optional dependencies in root `pyproject.toml`

2. **Shared vs agent-specific tools?**
   - Some tools might be agent-specific (e.g., quant-specific trading tools)
   - Could have `agents/quant/tools/` for agent-specific tools

3. **Versioning strategy?**
   - Single version for all agents?
   - Or per-agent versioning?

4. **Testing strategy?**
   - Unit tests per agent?
   - Integration tests?
   - Mock Nexus server for tests?

What do you think of this structure? Should we adjust anything before we start migrating?

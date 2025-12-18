# Nexus LangGraph Agents

> Collection of LangGraph agents with Nexus filesystem integration, deployable on LangGraph Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## Overview

This repository contains production-ready LangGraph agents that leverage Nexus filesystem for persistent storage, file operations, and multi-agent collaboration. All agents are designed for deployment on LangGraph Platform.

**Key Features:**
- ✅ Multiple specialized agents (ReAct, Quant Trading, Talent Search, etc.)
- ✅ Shared Nexus tools and utilities
- ✅ LangGraph Platform ready
- ✅ Python 3.11+ compatible
- ✅ Production deployment configurations

## Repository Structure

See [REPO_STRUCTURE.md](REPO_STRUCTURE.md) for detailed structure proposal.

```
nexus-langgraph/
├── agents/          # Individual agent implementations
├── shared/          # Shared utilities, tools, prompts
├── tests/           # Test suite
├── examples/        # Usage examples
└── langgraph.json   # Deployment configuration
```

## Available Agents

### ReAct Agent (`react`)
General-purpose ReAct agent with Nexus filesystem access.
- File search and analysis
- Code reading and writing
- Documentation generation

**Additional agents** (quant, talent, etc.) will be added in future updates.

## Quick Start

### Installation

```bash
git clone https://github.com/nexi-lab/nexus-langgraph.git
cd nexus-langgraph
pip install -e .
```

### Configuration

1. Copy `.env.example` to `.env`
2. Set your API keys:
   ```bash
   export NEXUS_API_KEY="sk-your-nexus-key"
   export ANTHROPIC_API_KEY="sk-ant-your-key"  # or OPENAI_API_KEY
   ```

### Deploy to LangGraph Platform

```bash
langgraph dev
```

Or deploy to LangGraph Cloud:
```bash
langgraph deploy
```

## Dependencies

- `nexus-fs-python[langgraph]>=0.1.0` - Nexus client SDK
- `langgraph>=0.2.0` - LangGraph framework
- `langchain-core>=0.3.0` - LangChain core
- `langchain-anthropic>=0.2.0` - Claude support
- `langchain-openai>=0.2.0` - GPT-4 support

## Documentation

- [Repository Structure](REPO_STRUCTURE.md) - Detailed structure proposal
- [Deployment Guide](docs/deployment.md) - LangGraph Platform deployment
- [Adding Agents](docs/adding_agents.md) - Guide for new agents
- [Architecture](docs/architecture.md) - System architecture

## Status

🚧 **In Planning** - Repository structure being finalized. Migration from `nexus/examples/langgraph` in progress.

## Related Projects

- [nexus-fs-python](https://github.com/nexi-lab/nexus-python) - Python client SDK
- [nexus](https://github.com/nexi-lab/nexus) - Nexus filesystem server

## License

Apache-2.0

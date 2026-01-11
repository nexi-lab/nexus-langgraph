#!/usr/bin/env python3
"""ReAct Agent using LangChain's create_agent.

This agent demonstrates how to use LangChain's create_agent function
to build a ReAct agent with Nexus filesystem integration.

Authentication:
    API keys are REQUIRED via metadata.x_auth: "Bearer <token>"
    Frontend automatically passes the authenticated user's API key in request metadata.
    Each tool extracts and uses the token to create an authenticated RemoteNexusFS instance.

Usage from Frontend (HTTP):
    POST http://localhost:2024/runs/stream
    {
        "assistant_id": "react",
        "input": {
            "messages": [{"role": "user", "content": "Find all Python files"}]
        },
        "metadata": {
            "x_auth": "Bearer sk-your-api-key-here",
            "user_id": "user-123",
            "tenant_id": "tenant-123",
            "workspace_path": "/tenant:multifi.ai/user:e1592bdf.../workspace/ws_build_606",  // Optional: current workspace
            "opened_file_path": "/workspace/admin/script.py"  // Optional: currently opened file
        }
    }

    Note: The frontend automatically includes x_auth, workspace_path, and opened_file_path in metadata when user is logged in.
"""

import logging
import os

from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig

from shared.config.llm_config import get_llm
from shared.tools.nexus_tools import get_nexus_fs_tools, get_nexus_sandbox_tools, get_web_tools

# Configure logging to show INFO level logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get configuration from environment variables
E2B_TEMPLATE_ID = os.getenv("E2B_TEMPLATE_ID")

# Check E2B configuration
if E2B_TEMPLATE_ID:
    print(f"E2B sandbox enabled with template: {E2B_TEMPLATE_ID}")
else:
    print("E2B sandbox disabled (E2B_TEMPLATE_ID not set)")


# LLM will be created lazily on first use (allows import without API keys)
_llm = None


def get_llm_instance():
    """Get or create LLM instance (lazy initialization)."""
    global _llm
    if _llm is None:
        _llm = get_llm()
    return _llm


# Create ReAct agent with dynamic prompt
# LangGraph Platform expects a factory function that takes RunnableConfig
async def agent(config: RunnableConfig):
    """
    Factory function to create the ReAct agent.

    LangGraph Platform calls this with a RunnableConfig to create the agent instance.
    The agent is created lazily when first needed (allows import without API keys).

    Args:
        config: Runtime configuration (provided by LangGraph Platform)

    Returns:
        Compiled LangGraph agent
    """
    from shared.prompts.react_prompt import get_system_prompt_async

    system_prompt_str = await get_system_prompt_async(config, role="general")

    tools = get_nexus_fs_tools() + get_web_tools()
    if config.get("metadata", {}).get("sandbox_id"):
        tools += get_nexus_sandbox_tools()

    return create_agent(
        model=get_llm_instance(),
        tools=tools,
        system_prompt=system_prompt_str,
    )

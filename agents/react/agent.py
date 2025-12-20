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
            "opened_file_path": "/workspace/admin/script.py"  // Optional: currently opened file
        }
    }

    Note: The frontend automatically includes x_auth and opened_file_path in metadata when user is logged in.
"""

import os

from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig

from shared.config.llm_config import get_llm
from shared.prompts.react_prompt import get_system_prompt_async
from shared.tools.nexus_tools import get_nexus_tools

# Get configuration from environment variables
E2B_TEMPLATE_ID = os.getenv("E2B_TEMPLATE_ID")

# Check E2B configuration
if E2B_TEMPLATE_ID:
    print(f"E2B sandbox enabled with template: {E2B_TEMPLATE_ID}")
else:
    print("E2B sandbox disabled (E2B_TEMPLATE_ID not set)")

# Create tools (no API key needed - will be passed per-request via metadata)
tools = get_nexus_tools()

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
def agent(config: RunnableConfig):
    """
    Factory function to create the ReAct agent.

    LangGraph Platform calls this with a RunnableConfig to create the agent instance.
    The agent is created lazily when first needed (allows import without API keys).

    Args:
        config: Runtime configuration (provided by LangGraph Platform)

    Returns:
        Compiled LangGraph agent
    """

    # Create a prompt function that LangGraph can call dynamically
    # This allows the prompt to be generated at runtime with access to state
    # The config is captured in the closure from the factory function
    def make_prompt_func(factory_config):
        """Create a prompt function with config captured in closure."""

        async def prompt_func(state):
            """Dynamic prompt function that LangGraph calls at runtime."""
            # Use the config from the factory function (captured in closure)
            # LangGraph will call this with state, and we use the factory config for auth
            return await get_system_prompt_async(factory_config, role="general", state=state)

        return prompt_func

    # Create the agent with the new create_agent API
    # LangGraph's create_agent supports async callables for system_prompt
    return create_agent(
        model=get_llm_instance(),
        tools=tools,
        system_prompt=make_prompt_func(config),  # Pass async callable instead of string
    )


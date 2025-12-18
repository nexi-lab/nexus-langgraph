#!/usr/bin/env python3
"""ReAct Agent using LangGraph's Prebuilt create_react_agent.

This agent demonstrates how to use LangGraph's prebuilt create_react_agent
function to quickly build a ReAct agent with Nexus filesystem integration.

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

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langgraph.prebuilt import create_react_agent

from shared.config.llm_config import get_llm
from shared.prompts.react_prompt import get_system_prompt
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

# Create LLM
llm = get_llm()


def build_prompt(state: dict, config: RunnableConfig) -> list:
    """Build prompt with optional opened file context from metadata.

    This function is called before each LLM invocation and can access
    the config which includes metadata from the frontend.

    Args:
        state: Current agent state
        config: Runtime configuration with metadata

    Returns:
        List of messages (system message + user messages)
    """
    # Get complete prompt with opened file context
    system_content = get_system_prompt(config, role="general", state=state)

    # Return system message + user messages
    return [SystemMessage(content=system_content)] + state["messages"]


# Create a runnable that wraps the prompt builder
prompt_runnable = RunnableLambda(build_prompt)

# Create prebuilt ReAct agent with dynamic prompt
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=prompt_runnable,
)

"""System prompts for ReAct agents.

This module provides system prompt generation using the official nexus.tools.get_prompt.
All prompts include skills list, workspace context, and opened file context.
"""

from langchain_core.runnables import RunnableConfig


async def get_system_prompt_async(
    config: RunnableConfig | None = None, role: str = "general", state: dict | None = None
) -> str:
    """Get system prompt using the official nexus.tools.get_prompt (REQUIRED).

    This function ONLY uses the official get_prompt from nexus.tools package.
    It includes skills list, workspace context, and opened file context.
    If nexus.tools is not available or any error occurs, this function will raise an exception.

    Args:
        config: Runtime configuration (provided by framework) containing auth metadata (REQUIRED)
        role: Agent role ("general", "coding", "analysis", etc.)
        state: Optional agent state (injected by LangGraph)

    Returns:
        System prompt string with skills, workspace, and file context included

    Raises:
        RuntimeError: If config is None
        ImportError: If nexus.tools package is not available
        Exception: Any error from nexus.tools.get_prompt will be propagated
    """
    if config is None:
        raise RuntimeError(
            "Config is required for get_system_prompt_async. "
            "Cannot generate prompt without config containing metadata."
        )

    # Import the official get_prompt (will raise ImportError if not available)
    try:
        from nexus.tools import get_prompt as get_nexus_prompt
    except ImportError as e:
        raise ImportError(
            "Failed to import nexus.tools.get_prompt. "
            "Ensure the nexus package is properly installed and available. "
            f"Original error: {e}"
        ) from e

    # Run sync function in thread pool to avoid blocking event loop
    import asyncio

    loop = asyncio.get_event_loop()

    try:
        return await loop.run_in_executor(
            None, lambda: get_nexus_prompt(config, role=role, state=state, include_opened_file=True)
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to generate system prompt using nexus.tools.get_prompt: {type(e).__name__}: {e}"
        ) from e

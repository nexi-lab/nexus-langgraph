"""System prompts for ReAct agents."""

from langchain_core.runnables import RunnableConfig


def _format_skills_prompt(skills_data: list) -> str:
    """Format skills data into a markdown prompt section.

    Args:
        skills_data: List of skill dictionaries with name, description, file_path, etc.

    Returns:
        Formatted markdown string describing available skills
    """
    if not skills_data:
        return ""

    prompt_lines = [
        "\n\n## Available Skills\n\n",
        "The following skills are available in the Nexus system that you can reference or use:\n\n",
    ]

    for i, skill in enumerate(skills_data, 1):
        name = skill.get("name", "Unknown")
        description = skill.get("description", "No description")
        file_path = skill.get("file_path", None)

        prompt_lines.append(f"{i}. **{name}**")
        prompt_lines[-1] += f"   {description}\n"
        if file_path:
            prompt_lines.append(f"   Path: `{file_path}`\n")
        prompt_lines.append("\n")

    prompt_lines.append(f"Total: {len(skills_data)} skills available\n")

    return "".join(prompt_lines)


async def _get_skills_prompt_async(config: RunnableConfig, state: dict | None = None) -> str:
    """Get skills prompt section asynchronously.

    Tries multiple methods to get skills:
    1. nexus.tools.get_skills_prompt (if available, sync wrapper)
    2. nexus_client.langgraph.tools.list_skills (async, preferred)
    3. Returns empty string if both fail

    Args:
        config: Runtime configuration containing auth metadata
        state: Optional agent state

    Returns:
        Formatted skills prompt section or empty string
    """
    # Try method 1: nexus.tools.get_skills_prompt (sync, preferred if available)
    try:
        from nexus.tools import get_skills_prompt

        # Run sync function in thread pool to avoid blocking
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: get_skills_prompt(config, state))
    except ImportError:
        pass

    # Try method 2: nexus_client.langgraph.tools.list_skills (async)
    try:
        from nexus_client.langgraph.tools import list_skills

        # Now we can use async directly - no need for thread pool!
        result = await list_skills(config, state, tier="all")
        skills_data = result.get("skills", [])
        return _format_skills_prompt(skills_data)
    except (ImportError, Exception) as e:
        # If skills listing fails, return empty string (don't break the agent)
        # Silently handle ImportError (expected when nexus_client not available)
        if isinstance(e, ImportError):
            return ""

        # Check if it's a connection error (expected when server is down)
        # Connection errors are common and expected, so we don't log them
        error_msg = str(e).lower()
        connection_keywords = ["connection", "refused", "connect", "timeout", "network", "errno 61", "failed to"]
        is_connection_error = any(keyword in error_msg for keyword in connection_keywords)

        # Only log non-connection errors (actual problems, not just server being down)
        if not is_connection_error:
            print(f"Warning: Could not fetch skills for prompt: {e}")
        return ""


async def get_system_prompt_async(
    config: RunnableConfig | None = None, role: str = "general", state: dict | None = None
) -> str:
    """Get system prompt asynchronously with optional opened file context and skills list.

    This is the async version that can be used as a callable for LangGraph's create_agent.
    It attempts to use the official get_prompt from nexus.tools which includes skills list.
    If that's not available, it falls back to fetching skills via nexus_client or a basic prompt.

    Args:
        config: Runtime configuration (provided by framework) containing auth metadata
        role: Agent role ("general", "coding", "analysis", etc.)
        state: Optional agent state (injected by LangGraph)

    Returns:
        System prompt string with skills list included (if available)

    Note:
        This function tries multiple methods to include skills:
        1. nexus.tools.get_prompt (preferred, includes skills automatically)
        2. nexus_client.langgraph.tools.list_skills (fallback, async)
        3. Basic prompt without skills (final fallback)
    """
    # Try to use the official get_prompt from nexus.tools (includes skills)
    # Only if config is provided (nexus.tools.get_prompt requires config)
    if config is not None:
        try:
            from nexus.tools import get_prompt as get_nexus_prompt

            # Run sync function in thread pool to avoid blocking
            import asyncio

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, lambda: get_nexus_prompt(config, role=role, state=state, include_opened_file=True)
            )
        except ImportError:
            pass  # Fall through to manual implementation

    # Fallback: Build prompt manually (when nexus.tools not available or config is None)
    base_prompt = "You are a helpful AI assistant with access to Nexus filesystem operations. "
    base_prompt += "You can search, read, write, and analyze files to help users with their tasks."

    # Add role-specific context
    if role == "coding":
        base_prompt += " You specialize in code analysis, debugging, and software development tasks."
    elif role == "analysis":
        base_prompt += " You specialize in data analysis, research, and information synthesis."

    # Add skills section if config is available (now async!)
    skills_section = ""
    if config:
        try:
            skills_section = await _get_skills_prompt_async(config, state)
        except Exception as e:
            # If skills fetching fails, continue without skills
            # Don't log connection errors (expected when server is down)
            error_msg = str(e).lower()
            is_connection_error = any(
                keyword in error_msg
                for keyword in ["connection", "refused", "connect", "timeout", "network", "errno 61"]
            )
            if not is_connection_error:
                print(f"Warning: Could not fetch skills: {e}")

    # Add opened file context if available
    opened_file_section = ""
    if config:
        metadata = config.get("metadata", {}) if hasattr(config, "get") else getattr(config, "metadata", {})
        opened_file = metadata.get("opened_file_path") if isinstance(metadata, dict) else None
        if opened_file:
            opened_file_section = f"\n\nCurrently viewing file: {opened_file}"

    return base_prompt + skills_section + opened_file_section


def get_system_prompt(config: RunnableConfig | None = None, role: str = "general", state: dict | None = None) -> str:
    """Get system prompt synchronously (backward compatibility wrapper).

    This is a sync wrapper around the async version. For new code, prefer using
    get_system_prompt_async directly or pass it as a callable to create_agent.

    Args:
        config: Runtime configuration (provided by framework) containing auth metadata
        role: Agent role ("general", "coding", "analysis", etc.)
        state: Optional agent state (injected by LangGraph)

    Returns:
        System prompt string with skills list included (if available)
    """
    import asyncio

    # Try to use existing event loop if available
    try:
        loop = asyncio.get_running_loop()
        # If we're in an async context, we can't use asyncio.run()
        # In this case, we'll need to use the async version directly
        # For now, return a basic prompt (caller should use async version)
        base_prompt = "You are a helpful AI assistant with access to Nexus filesystem operations. "
        base_prompt += "You can search, read, write, and analyze files to help users with their tasks."
        return base_prompt
    except RuntimeError:
        # No running loop, we can use asyncio.run()
        return asyncio.run(get_system_prompt_async(config, role=role, state=state))


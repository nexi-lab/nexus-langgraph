"""System prompts for ReAct agents."""

import asyncio

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


def _get_skills_prompt_sync(config: RunnableConfig, state: dict | None = None) -> str:
    """Get skills prompt section synchronously.
    
    Tries multiple methods to get skills:
    1. nexus.tools.get_skills_prompt (if available)
    2. nexus_client.langgraph.tools.list_skills (async, run in event loop)
    3. Returns empty string if both fail
    
    Args:
        config: Runtime configuration containing auth metadata
        state: Optional agent state
    
    Returns:
        Formatted skills prompt section or empty string
    """
    # Try method 1: nexus.tools.get_skills_prompt (sync, preferred)
    try:
        from nexus.tools import get_skills_prompt
        return get_skills_prompt(config, state)
    except ImportError:
        pass
    
    # Try method 2: nexus_client.langgraph.tools.list_skills (async)
    try:
        from nexus_client.langgraph.tools import list_skills
        
        # Run async function in event loop
        # Check if there's already a running event loop
        try:
            # Try to get the running loop (Python 3.7+)
            asyncio.get_running_loop()
            # If we get here, there's a running loop, so we can't use asyncio.run()
            # In this case, we'll skip skills for now (prompt will be built without skills)
            # This is a limitation when called from an async context
            return ""
        except RuntimeError:
            # No running loop, we can create a new one with asyncio.run()
            pass
        
        # Run the async function (we know there's no running loop at this point)
        result = asyncio.run(list_skills(config, state, tier="all"))
        skills_data = result.get("skills", [])
        return _format_skills_prompt(skills_data)
    except (ImportError, Exception) as e:
        # If skills listing fails, return empty string (don't break the agent)
        print(f"Warning: Could not fetch skills for prompt: {e}")
        return ""


def get_system_prompt(config: RunnableConfig | None = None, role: str = "general", state: dict | None = None) -> str:
    """Get system prompt with optional opened file context from metadata and skills list.

    This function attempts to use the official get_prompt from nexus.tools which includes
    skills list. If that's not available, it falls back to fetching skills via nexus_client
    or a basic prompt without skills.

    Args:
        config: Runtime configuration (provided by framework) containing auth metadata
        role: Agent role ("general", "coding", "analysis", etc.)
        state: Optional agent state (injected by LangGraph)

    Returns:
        System prompt string with skills list included (if available)

    Note:
        This function tries multiple methods to include skills:
        1. nexus.tools.get_prompt (preferred, includes skills automatically)
        2. nexus_client.langgraph.tools.list_skills (fallback)
        3. Basic prompt without skills (final fallback)
    """
    # Try to use the official get_prompt from nexus.tools (includes skills)
    # Only if config is provided (nexus.tools.get_prompt requires config)
    if config is not None:
        try:
            from nexus.tools import get_prompt as get_nexus_prompt
            
            # Use the official prompt function which includes skills and opened file context
            return get_nexus_prompt(config, role=role, state=state, include_opened_file=True)
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

    # Add skills section if config is available
    skills_section = ""
    if config:
        try:
            skills_section = _get_skills_prompt_sync(config, state)
        except Exception as e:
            # If skills fetching fails, continue without skills
            print(f"Warning: Could not fetch skills: {e}")
    
    # Add opened file context if available
    opened_file_section = ""
    if config:
        metadata = config.get("metadata", {}) if hasattr(config, "get") else getattr(config, "metadata", {})
        opened_file = metadata.get("opened_file_path") if isinstance(metadata, dict) else None
        if opened_file:
            opened_file_section = f"\n\nCurrently viewing file: {opened_file}"

    return base_prompt + skills_section + opened_file_section

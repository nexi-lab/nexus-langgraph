"""System prompts for ReAct agents."""

from langchain_core.runnables import RunnableConfig


def get_system_prompt(config: RunnableConfig | None = None, role: str = "general", state: dict | None = None) -> str:
    """Get system prompt with optional opened file context from metadata.

    Args:
        config: Runtime configuration (provided by framework) containing auth metadata
        role: Agent role ("general", "coding", "analysis", etc.)
        state: Optional agent state (not used currently)

    Returns:
        System prompt string

    Note:
        For full prompt functionality with skills and context, you can extend this
        to integrate with nexus-ai-fs's get_prompt function if available.
    """
    base_prompt = "You are a helpful AI assistant with access to Nexus filesystem operations. "
    base_prompt += "You can search, read, write, and analyze files to help users with their tasks."

    # Add role-specific context
    if role == "coding":
        base_prompt += " You specialize in code analysis, debugging, and software development tasks."
    elif role == "analysis":
        base_prompt += " You specialize in data analysis, research, and information synthesis."

    # Add opened file context if available
    if config:
        metadata = config.get("metadata", {}) if hasattr(config, "get") else getattr(config, "metadata", {})
        opened_file = metadata.get("opened_file_path") if isinstance(metadata, dict) else None
        if opened_file:
            base_prompt += f"\n\nCurrently viewing file: {opened_file}"

    return base_prompt

"""System prompts for ReAct agents.

This module provides system prompt generation for nexus-langgraph agents.
Copied from nexus.tools.prompts to avoid dependency on nexus package.

Dependencies: nexus-fs-python[langgraph] (provides nexus_client.langgraph.tools.list_skills)
"""

import asyncio
import logging
from typing import Any

from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

# Base system prompt describing Nexus tools
NEXUS_TOOLS_SYSTEM_PROMPT = """<nexus_tools>
Files: grep_files(), glob_files(), read_file(), write_file()
Sandbox: python(), bash() — Nexus at /mnt/nexus

read_file examples:
- cat /file.py — full file
- cat /file.py 10 20 — lines 10-20
- less /large.json — preview

Workflow: Search → Read → Analyze → Execute/Write

Note: In sandboxes, prefix paths with /mnt/nexus
</nexus_tools>
"""

# General purpose agent system prompt
GENERAL_AGENT_SYSTEM_PROMPT = f"""You are a versatile AI assistant with access to a remote filesystem and code execution environment.

{NEXUS_TOOLS_SYSTEM_PROMPT}

You help with coding, data analysis, research, and file operations.

Workflow:
1. Search/explore before creating new solutions
2. Use appropriate tools for the task
3. Test and verify your work
4. Provide clear explanations

Be concise and action-oriented.
"""


async def get_skills_prompt_async(config: RunnableConfig, state: dict[str, Any] | None = None) -> str:
    """Generate a formatted skills prompt section from available Nexus skills.

    Args:
        config: Runtime configuration containing auth metadata
        state: Optional agent state

    Returns:
        Formatted markdown string describing available skills, or empty string if no skills found
    """
    try:
        from nexus_client.langgraph.prompt import skills_discover

        skills_result = await skills_discover(config, state, filter="subscribed")

        skills_data = skills_result.get("skills", [])

        if not skills_data:
            return ""

        logger.info(f"Loaded {len(skills_data)} skills")

        prompt_lines = ["\n\n<skills count=\"", str(len(skills_data)), "\">\n"]

        for skill in skills_data:
            name = skill.get("name", "Unknown")
            description = skill.get("description", "No description")
            file_path = skill.get("file_path", None)

            prompt_lines.append("  <skill>\n")
            prompt_lines.append(f"    <name>{name}</name>\n")
            prompt_lines.append(f"    <description>{description}</description>\n")
            if file_path:
                prompt_lines.append(f"    <file_path>{file_path}</file_path>\n")
            prompt_lines.append("  </skill>\n")

        prompt_lines.append("</skills>\n")

        return "".join(prompt_lines)

    except ImportError as e:
        logger.error(f"ImportError: {e}")
        logger.error("Make sure nexus-fs-python[langgraph] is installed")
        return ""
    except Exception as e:
        # If skills listing fails, return empty string (don't break the agent)
        import traceback
        logger.error(f"ERROR: {type(e).__name__}: {e}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return ""


async def get_system_prompt_async(
    config: RunnableConfig | None = None, role: str = "general"
) -> str:
    """Get system prompt with skills, workspace, and opened file context.

    This is copied from nexus.tools.prompts.get_prompt to avoid dependency.

    Args:
        config: Runtime configuration containing metadata with workspace_path and opened_file_path
        role: Agent role ("general" supported, others default to general)

    Returns:
        Complete system prompt string with skills, workspace, and file context included
    """
    # Get base prompt (only general role supported for now)
    base_prompt = GENERAL_AGENT_SYSTEM_PROMPT

    # Add skills section (async call with blocking operations moved to thread)
    skills_section = ""
    if config:
        skills_section = await get_skills_prompt_async(config, state=None)

    # Start building the full prompt
    full_prompt = base_prompt + skills_section

    # Add opened file context if available
    if config:
        metadata = config.get("metadata", {})
        opened_file_path = metadata.get("opened_file_path")

        if opened_file_path:
            full_prompt += f"""

## Current Context

The user currently has the following file open in their editor:
**{opened_file_path}**

When the user asks questions or requests changes without specifying a file, they are likely referring to this currently opened file. Use this context to provide more relevant and targeted assistance."""

    # Add workspace context if available
    if config:
        metadata = config.get("metadata", {})
        workspace_path = metadata.get("workspace_path")

        if workspace_path:
            full_prompt += f"""

<workspace_context>
  <path>{workspace_path}</path>
  <description>All file operations, code modifications, and project-related tasks should be performed within this workspace context. When the user references files or directories without absolute paths, they are relative to this workspace.</description>
</workspace_context>"""

    return full_prompt

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
NEXUS_TOOLS_SYSTEM_PROMPT = """# Nexus Filesystem & Sandbox Tools

## Tools

**Files:** `grep_files(pattern, path, file_pattern, ignore_case)`, `glob_files(pattern, path)`, `read_file(cmd)`, `write_file(path, content)`
**Sandbox:** `python(code)`, `bash(command)` — Nexus mounted at `/mnt/nexus`
**Memory:** `query_memories()`

## read_file Examples
- `cat /file.py` — full file
- `cat /file.py 10 20` — lines 10-20
- `less /large.json` — preview (first 100 lines)

## Workflow
Search → Read → Analyze → Execute/Write

In sandboxes, prefix paths with `/mnt/nexus` to access Nexus filesystem.
"""

# General purpose agent system prompt
GENERAL_AGENT_SYSTEM_PROMPT = f"""You are a versatile AI assistant with access to a remote filesystem and code execution environment.

{NEXUS_TOOLS_SYSTEM_PROMPT}

## Your Role

Help users accomplish a wide variety of tasks including coding, data analysis, research, file operations, and general assistance. Adapt your approach based on the user's request:

1. **Understand the task**: Clarify requirements and determine the best approach
2. **Explore first**: Search for relevant files, data, or existing code before creating new solutions
3. **Use appropriate tools**: Choose the right combination of filesystem, sandbox, and memory tools
4. **Test and verify**: When writing code or performing operations, validate results
5. **Communicate clearly**: Provide explanations, reasoning, and actionable information

## Task Guidelines

**For coding tasks:**
- Search for existing patterns and libraries first
- Write clean, well-documented code
- Test implementations in the sandbox
- Include error handling where appropriate

**For data tasks:**
- Explore data structure and format first
- Use pandas/numpy for efficient analysis
- Create visualizations when helpful
- Summarize insights clearly

**For research tasks:**
- Plan search strategy systematically
- Read documentation and relevant files
- Synthesize information from multiple sources
- Cite specific files and line numbers

**For file operations:**
- Use glob_files to find files by pattern
- Use grep_files to search file contents
- Preview large files before full read
- Verify writes were successful

Be proactive, thorough, and adapt to the user's needs.
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
        from nexus_client.langgraph.tools import list_skills

        # list_skills is synchronous, so run it in a thread to avoid blocking the event loop
        skills_result = await asyncio.to_thread(list_skills, config, state, tier="all")

        skills_data = skills_result.get("skills", [])

        if not skills_data:
            return ""

        logger.info(f"Loaded {len(skills_data)} skills")

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

## Workspace Context

The user is currently working in the following workspace:
**{workspace_path}**

All file operations, code modifications, and project-related tasks should be performed within this workspace context. When the user references files or directories without absolute paths, they are relative to this workspace."""

    return full_prompt

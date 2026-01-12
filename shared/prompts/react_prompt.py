"""System prompts for ReAct agents.

This module provides system prompt generation for nexus-langgraph agents.
Copied from nexus.tools.prompts to avoid dependency on nexus package.

Dependencies: nexus-fs-python[langgraph] (provides nexus_client.langgraph.tools.list_skills)
"""

import logging
from typing import Any

from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

# Base system prompt describing Nexus tools
NEXUS_TOOLS_SYSTEM_PROMPT = """<nexus_tools>
Files: grep_files(), glob_files(), read_file(), write_file()
- Read file CANNOT read binary files (e.g. pdf, excel, doc, etc.) directly, you need to use the parsed path format to get the parsed markdown.
- To get the markdown of a binary file, use the parsed path format: /path/to/file.ext -> /path/to/file_parsed.ext.md
- E.g. /path/to/file.pdf -> /path/to/file_parsed.pdf.md, /path/to/file.xlsx -> /path/to/file_parsed.xlsx.md, /path/to/file.doc -> /path/to/file_parsed.doc.md, etc.

Sandbox(optional): python(), bash()
- To access files inside Nexus, you MUST add prefix /mnt/nexus to the path.

Workflow: Search → Read → Analyze → Execute/Write

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

    Checks for assigned_skills in metadata first. If present and non-empty,
    uses those skills. Otherwise falls back to discovering all subscribed skills.

    Args:
        config: Runtime configuration containing auth metadata and assigned_skills
        state: Optional agent state

    Returns:
        Formatted markdown string describing available skills, or empty string if no skills found
    """
    try:
        # Check for assigned_skills in metadata first
        metadata = config.get("metadata", {}) if config else {}
        assigned_skills = metadata.get("assigned_skills", [])

        skills_data = []

        if assigned_skills and len(assigned_skills) > 0:
            # Use assigned skills from metadata
            logger.info(f"Using {len(assigned_skills)} assigned skills from metadata")

            # assigned_skills format: [{name, description, path}]
            # Convert to skills_data format expected by the prompt builder
            for skill in assigned_skills:
                skills_data.append({
                    "name": skill.get("name", "Unknown"),
                    "description": skill.get("description", "No description"),
                    "file_path": skill.get("path", None)
                })
        else:
            # Fall back to discovering all subscribed skills
            logger.info("No assigned skills in metadata, discovering subscribed skills")
            from nexus_client.langgraph.prompt import skills_discover

            skills_result = await skills_discover(config, state, filter="subscribed")
            skills_data = skills_result.get("skills", [])

        if not skills_data:
            return ""

        logger.info(f"Loaded {len(skills_data)} skills for prompt")

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


async def get_connectors_prompt_async(config: RunnableConfig, state: dict[str, Any] | None = None) -> str:
    """Generate a formatted connectors prompt section from active Nexus connectors.

    Args:
        config: Runtime configuration containing auth metadata
        state: Optional agent state

    Returns:
        Formatted XML string describing available connectors, or empty string if no connectors found
    """
    try:
        from nexus_client.langgraph.tools import list_connectors

        # list_connectors returns all mounts, filter for connector backends only
        all_mounts = await list_connectors(config, state)

        # Filter to only connector backends (exclude LocalBackend, etc.)
        connector_backends = ["GmailConnectorBackend", "SlackConnectorBackend",
                            "GDriveConnectorBackend", "XConnectorBackend"]
        connectors_data = [
            mount for mount in all_mounts
            if mount.get("backend_type") in connector_backends
        ]

        if not connectors_data:
            return ""

        logger.info(f"Loaded {len(connectors_data)} active connectors for prompt")

        # Map backend types to human-readable names and descriptions
        connector_info = {
            "GmailConnectorBackend": ("Gmail", "Access your Gmail messages and threads"),
            "SlackConnectorBackend": ("Slack", "Access Slack channels, DMs, and messages"),
            "GDriveConnectorBackend": ("Google Drive", "Access Google Drive files and folders"),
            "XConnectorBackend": ("X (Twitter)", "Access X/Twitter posts and timeline"),
        }

        prompt_lines = ["\n\n<connectors count=\"", str(len(connectors_data)), "\">\n"]

        for conn in connectors_data:
            mount_point = conn.get("mount_point", "Unknown")
            backend_type = conn.get("backend_type", "Unknown")
            readonly = conn.get("readonly", False)

            # Get friendly name and description
            friendly_name, description = connector_info.get(
                backend_type, (backend_type, "Third-party service integration")
            )

            prompt_lines.append("  <connector>\n")
            prompt_lines.append(f"    <name>{friendly_name}</name>\n")
            prompt_lines.append(f"    <description>{description}</description>\n")
            prompt_lines.append(f"    <mount_point>{mount_point}</mount_point>\n")
            prompt_lines.append(f"    <backend_type>{backend_type}</backend_type>\n")
            if readonly:
                prompt_lines.append("    <readonly>true</readonly>\n")
            prompt_lines.append("  </connector>\n")

        prompt_lines.append("</connectors>\n")

        return "".join(prompt_lines)

    except ImportError as e:
        logger.error(f"ImportError: {e}")
        logger.error("Make sure nexus-fs-python[langgraph] is installed")
        return ""
    except Exception as e:
        # If connector listing fails, return empty string (don't break the agent)
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

    # Add connectors section
    connectors_section = ""
    if config:
        connectors_section = await get_connectors_prompt_async(config, state=None)

    # Start building the full prompt
    full_prompt = base_prompt + skills_section + connectors_section

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

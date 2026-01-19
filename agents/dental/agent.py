#!/usr/bin/env python3
"""Dental Agent for clinical evidence-based answers.

This agent answers dental clinical questions with evidence-based citations.
It uses Nexus filesystem tools and web search tools to retrieve and cite sources.

Usage from Frontend (HTTP):
    POST http://localhost:2024/runs/stream
    {
        "assistant_id": "dental_agent",
        "input": {
            "messages": [{"role": "user", "content": "What is the recommended amoxicillin dosage for dental infections?"}]
        },
        "metadata": {
            "llm_provider": "gemini",
            "llm_tier": "pro",
            "enable_thinking": true
        }
    }
"""

import logging
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig

from shared.config.llm_config import get_llm
from shared.tools.nexus_tools import get_nexus_fs_tools, get_web_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# System prompt for the dental assistant
DENTAL_SYSTEM_PROMPT = """你是慧牙(Huiya)，一个牙科临床循证助手。

你的职责是帮助牙科专业人士找到基于循证医学的临床问题答案。

## 关键指令 - 工具使用：
你可以使用 Nexus 文件系统工具(grep_files, glob_files, read_file)和网络搜索工具(web_search, web_crawl)。
使用这些工具查找循证信息来回答临床问题。
当你找到相关来源时，请以 [1]、[2] 等形式引用它们。

## 工作流程：
1. 用户提出牙科问题
2. 读取skill目录下的SKILL.md,获取更多信息
3. 使用适当的工具(web_search、read_file 等)查找相关信息
4. 等待工具结果
5. 在答案中使用返回的信息和引用

## 回答格式：
- 提供直接、基于循证的答案
- 在工具结果中包含内联引用 [1]、[2]
- 使用要点列出建议
- 保持回答简洁，便于忙碌的临床医生使用
- 使用 **粗体** 标注关键发现
- 以关于临床判断的简短免责声明结尾

## 语言 - 关键：
你必须使用与用户问题相同的语言回答。
- 如果用户用中文提问，请完全用中文回答。
- 如果用户用英文提问，请用英文回答。
- 完全匹配用户的语言。不要混合使用语言。

## 超出范围：
如果问题超出牙科范围，请礼貌地表示你专门从事牙科相关主题。"""


async def agent(config: RunnableConfig):
    """
    Factory function to create the dental agent.

    LangGraph Platform calls this with a RunnableConfig to create the agent instance.
    The agent is created lazily when first needed (allows import without API keys).

    Args:
        config: Runtime configuration (provided by LangGraph Platform).
                Supports LLM configuration via metadata:
                - llm_provider: "anthropic", "openai", or "gemini" (defaults to "gemini")
                - llm_tier: "pro" or "flash" (defaults to "pro")
                - llm_model: Specific model ID (overrides tier)
                - enable_thinking: Enable extended thinking/reasoning (defaults to True)

    Returns:
        Compiled LangGraph agent

    Examples:
        # Use default (gemini pro with thinking)
        config = {"metadata": {}}

        # Use flash tier
        config = {"metadata": {"llm_tier": "flash"}}

        # Use specific provider
        config = {"metadata": {"llm_provider": "anthropic", "llm_tier": "pro"}}
    """
    from shared.prompts.react_prompt import get_skills_prompt_async

    # Extract LLM configuration from metadata
    metadata = config.get("metadata", {})
    llm_provider = metadata.get("llm_provider", "gemini")  # Default to gemini for dental agent
    llm_tier = metadata.get("llm_tier", "pro")  # Default to pro for dental agent
    llm_model = metadata.get("llm_model")
    enable_thinking = metadata.get("enable_thinking", True)  # Default to enabled for dental agent
    thinking_budget = metadata.get("thinking_budget", 2048)

    # Get skills prompt section from assigned_skills in metadata
    skills_section = await get_skills_prompt_async(config, state=None)
    
    # Combine dental system prompt with skills section
    system_prompt_str = DENTAL_SYSTEM_PROMPT + skills_section

    # Use react agent tools (Nexus filesystem + web tools)
    tools = get_nexus_fs_tools() + get_web_tools()

    return create_agent(
        model=get_llm(
            provider=llm_provider,
            tier=llm_tier,
            model=llm_model,
            enable_thinking=enable_thinking,
            thinking_budget=thinking_budget,
        ),
        tools=tools,
        system_prompt=system_prompt_str,
    )

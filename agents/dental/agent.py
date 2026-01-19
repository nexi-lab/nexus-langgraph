#!/usr/bin/env python3
"""Dental Agent for clinical evidence-based answers.

This agent answers dental clinical questions with evidence-based citations.
It uses the search_dental_literature tool to retrieve and cite sources.

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
from agents.dental.tools import search_dental_literature

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# System prompt for the dental assistant
DENTAL_SYSTEM_PROMPT = """You are Huiya (慧牙), a dental clinical evidence assistant.

Your role is to help dental professionals find evidence-based answers to clinical questions.

## CRITICAL INSTRUCTION - TOOL USAGE:
You MUST call the search_dental_literature tool BEFORE answering ANY clinical question.
Do NOT skip the tool call. Do NOT mention the tool in your response text.
The tool will return citations that you should reference as [1], [2], etc.

## WORKFLOW:
1. User asks a dental question
2. YOU MUST CALL search_dental_literature with a relevant search query
3. Wait for tool results
4. Use the returned citations in your answer

## RESPONSE FORMAT:
- Provide direct, evidence-based answers
- Include inline citations [1], [2] from the tool results
- Use bullet points for lists of recommendations
- Keep responses focused and actionable for busy clinicians
- Use **bold** for key findings
- End with a brief disclaimer about clinical judgment

## LANGUAGE - CRITICAL:
You MUST respond in the SAME language as the user's question.
- If the user asks in Chinese (中文), respond ENTIRELY in Chinese.
- If the user asks in English, respond in English.
- Match the user's language exactly. Do NOT mix languages.

## OUT OF SCOPE:
If a question is outside dental scope, politely indicate you specialize in dental topics."""


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
    # Extract LLM configuration from metadata
    metadata = config.get("metadata", {})
    llm_provider = metadata.get("llm_provider", "gemini")  # Default to gemini for dental agent
    llm_tier = metadata.get("llm_tier", "pro")  # Default to pro for dental agent
    llm_model = metadata.get("llm_model")
    enable_thinking = metadata.get("enable_thinking", True)  # Default to enabled for dental agent
    thinking_budget = metadata.get("thinking_budget", 2048)

    tools = [search_dental_literature]

    return create_agent(
        model=get_llm(
            provider=llm_provider,
            tier=llm_tier,
            model=llm_model,
            enable_thinking=enable_thinking,
            thinking_budget=thinking_budget,
        ),
        tools=tools,
        system_prompt=DENTAL_SYSTEM_PROMPT,
    )

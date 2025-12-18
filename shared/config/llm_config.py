"""LLM provider configuration utilities."""

import os

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


def get_llm(model: str | None = None, provider: str | None = None):
    """
    Get LLM instance based on available API keys.

    Tries providers in this order:
    1. Anthropic (if ANTHROPIC_API_KEY is set)
    2. OpenAI (if OPENAI_API_KEY is set)
    3. OpenRouter (if OPENROUTER_API_KEY is set)

    Args:
        model: Optional model name (uses provider default if not specified)
        provider: Optional provider name to force ("anthropic", "openai", "openrouter")

    Returns:
        ChatModel instance

    Raises:
        ValueError: If no API keys are found
    """
    # Force provider if specified
    if provider == "anthropic" or (not provider and os.getenv("ANTHROPIC_API_KEY")):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            return ChatAnthropic(
                model=model or "claude-sonnet-4-5-20250929",
                max_tokens=10000,
            )

    if provider == "openai" or (not provider and os.getenv("OPENAI_API_KEY")):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return ChatOpenAI(
                model=model or "gpt-4-turbo-preview",
                temperature=0.7,
            )

    if provider == "openrouter" or (not provider and os.getenv("OPENROUTER_API_KEY")):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            # OpenRouter uses OpenAI client with base_url override
            return ChatOpenAI(
                model=model or "anthropic/claude-3.5-sonnet",
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                default_headers={"HTTP-Referer": "https://github.com/nexi-lab/nexus-langgraph"},
            )

    raise ValueError(
        "No LLM API key found. Set one of: ANTHROPIC_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY"
    )

"""LLM provider configuration utilities."""

import os
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


# Anthropic Models
CLAUDE_OPUS_4_5 = "claude-opus-4-5-20251101"
CLAUDE_SONNET_4_5 = "claude-sonnet-4-5-20250929"

# OpenAI Models
GPT_5_2 = "gpt-5.2"
GPT_5_MINI = "gpt-5-mini"

# Gemini Models
GEMINI_3_PRO = "gemini-3-pro-preview"
GEMINI_3_FLASH = "gemini-3-flash-preview"

# Model tier mappings
MODEL_TIERS = {
    "anthropic": {
        "pro": CLAUDE_OPUS_4_5,
        "flash": CLAUDE_SONNET_4_5,
    },
    "openai": {
        "pro": GPT_5_2,
        "flash": GPT_5_MINI,
    },
    "gemini": {
        "pro": GEMINI_3_PRO,
        "flash": GEMINI_3_FLASH,
    },
}


def get_llm(
    model: str | None = None,
    provider: str | None = None,
    tier: Literal["pro", "flash"] | None = None,
    enable_thinking: bool = False,
    thinking_budget: int = 2048,
):
    """
    Get LLM instance based on available API keys.

    Tries providers in this order:
    1. Anthropic (if ANTHROPIC_API_KEY is set)
    2. OpenAI (if OPENAI_API_KEY is set)
    3. Google Gemini (if GOOGLE_API_KEY is set)

    Args:
        model: Optional specific model ID (overrides tier selection)
        provider: Optional provider name ("anthropic", "openai", "gemini")
        tier: Optional tier selection ("pro" or "flash"). Defaults to "flash" if not specified.
        enable_thinking: Enable extended thinking/reasoning (currently only for Claude)
        thinking_budget: Token budget for thinking (minimum 1024, default 2048)

    Returns:
        ChatModel instance

    Raises:
        ValueError: If no API keys are found

    Examples:
        >>> # Use default flash tier for each provider
        >>> llm = get_llm(provider="anthropic")  # Claude Sonnet 4.5
        >>> llm = get_llm(provider="openai")     # GPT-5 Mini
        >>> llm = get_llm(provider="gemini")     # Gemini 3 Flash

        >>> # Use pro tier for more advanced capabilities
        >>> llm = get_llm(provider="anthropic", tier="pro")  # Claude Opus 4.5
        >>> llm = get_llm(provider="openai", tier="pro")     # GPT-5.2
        >>> llm = get_llm(provider="gemini", tier="pro")     # Gemini 3 Pro

        >>> # Enable extended thinking for Claude
        >>> llm = get_llm(provider="anthropic", enable_thinking=True, thinking_budget=4096)
    """
    # Determine which model to use
    def get_model_for_provider(prov: str) -> str:
        if model:
            return model
        if tier and prov in MODEL_TIERS:
            return MODEL_TIERS[prov][tier]
        # Default to flash tier
        return MODEL_TIERS.get(prov, {}).get("flash", "")

    # Force provider if specified
    if provider == "anthropic" or (not provider and os.getenv("ANTHROPIC_API_KEY")):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            selected_model = get_model_for_provider("anthropic")
            kwargs = {
                "model": selected_model,
                "max_tokens": 10000,
            }

            # Enable extended thinking if requested (minimum 1024 tokens)
            if enable_thinking:
                kwargs["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": max(1024, thinking_budget)
                }

            return ChatAnthropic(**kwargs)

    if provider == "openai" or (not provider and os.getenv("OPENAI_API_KEY")):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            selected_model = get_model_for_provider("openai")
            kwargs = {
                "model": selected_model,
                "temperature": 0.7,
            }

            # Enable reasoning for OpenAI reasoning models (o1, o3, o4-mini)
            # Only applies to reasoning models, ignored by others
            if enable_thinking:
                kwargs["reasoning_effort"] = "high"  # Options: minimal, low, medium, high

            return ChatOpenAI(**kwargs)

    if provider == "gemini" or (not provider and os.getenv("GOOGLE_API_KEY")):
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            selected_model = get_model_for_provider("gemini")
            kwargs = {
                "model": selected_model,
                "temperature": 0.7,
            }

            # Enable thinking for Gemini models
            # Gemini 2.5: uses thinking_budget (tokens)
            # Gemini 3+: uses thinking_level
            if enable_thinking:
                kwargs["thinking_budget"] = thinking_budget if thinking_budget > 0 else -1  # -1 = dynamic
                kwargs["include_thoughts"] = True  # Include thinking in response

            return ChatGoogleGenerativeAI(**kwargs)

    raise ValueError("No LLM API key found. Set one of: ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY")






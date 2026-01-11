#!/usr/bin/env python3
"""Example: Using ReAct Agent with different LLM configurations.

This example demonstrates how to configure the LLM provider and tier
when using the ReAct agent.
"""

import asyncio
import os

from langchain_core.runnables import RunnableConfig

# Set your API keys
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-key"
os.environ["OPENAI_API_KEY"] = "your-openai-key"
os.environ["GOOGLE_API_KEY"] = "your-google-key"


async def example_default_config():
    """Example 1: Use default configuration (auto-detected provider, flash tier)."""
    from agents.react.agent import agent

    print("=" * 60)
    print("Example 1: Default Configuration")
    print("=" * 60)

    config: RunnableConfig = {
        "metadata": {"x_auth": "Bearer your-token"},
    }

    agent_instance = await agent(config)
    print(f"Agent created with default LLM")
    print()


async def example_provider_flash():
    """Example 2: Specify provider with flash tier (default)."""
    from agents.react.agent import agent

    print("=" * 60)
    print("Example 2: Anthropic Flash (Claude Sonnet 4.5)")
    print("=" * 60)

    config: RunnableConfig = {
        "metadata": {
            "x_auth": "Bearer your-token",
            "llm_provider": "anthropic",
        },
    }

    agent_instance = await agent(config)
    print(f"Agent created with Anthropic Flash tier")
    print()


async def example_provider_pro():
    """Example 3: Use pro tier for advanced capabilities."""
    from agents.react.agent import agent

    print("=" * 60)
    print("Example 3: OpenAI Pro (GPT-5.2)")
    print("=" * 60)

    config: RunnableConfig = {
        "metadata": {
            "x_auth": "Bearer your-token",
            "llm_provider": "openai",
            "llm_tier": "pro",
        },
    }

    agent_instance = await agent(config)
    print(f"Agent created with OpenAI Pro tier")
    print()


async def example_specific_model():
    """Example 4: Use specific model ID."""
    from agents.react.agent import agent

    print("=" * 60)
    print("Example 4: Specific Model (Gemini 3 Pro)")
    print("=" * 60)

    config: RunnableConfig = {
        "metadata": {
            "x_auth": "Bearer your-token",
            "llm_model": "gemini-3-pro-preview",
            "llm_provider": "gemini",
        },
    }

    agent_instance = await agent(config)
    print(f"Agent created with specific Gemini 3 Pro model")
    print()


async def example_extended_thinking():
    """Example 5: Enable extended thinking for Claude."""
    from agents.react.agent import agent

    print("=" * 60)
    print("Example 5: Extended Thinking (Claude)")
    print("=" * 60)

    config: RunnableConfig = {
        "metadata": {
            "x_auth": "Bearer your-token",
            "llm_provider": "anthropic",
            "llm_tier": "flash",
            "enable_thinking": True,  # Enable extended thinking
            "thinking_budget": 2048,  # Token budget for thinking (min 1024)
        },
    }

    agent_instance = await agent(config)
    print(f"Agent created with extended thinking enabled")
    print()


async def example_thinking_all_providers():
    """Example 6: Extended thinking for all providers."""
    from agents.react.agent import agent

    print("=" * 60)
    print("Example 6: Extended Thinking (All Providers)")
    print("=" * 60)

    providers = ["anthropic", "openai", "gemini"]

    for provider in providers:
        print(f"\n{provider.capitalize()}:")
        config: RunnableConfig = {
            "metadata": {
                "x_auth": "Bearer your-token",
                "llm_provider": provider,
                "enable_thinking": True,
                "thinking_budget": 2048,
            },
        }
        agent_instance = await agent(config)
        print(f"  ✓ Agent created with thinking enabled")

    print()


async def example_http_request():
    """Example 7: HTTP request format for LangGraph Platform."""
    print("=" * 60)
    print("Example 7: HTTP Request Format")
    print("=" * 60)

    request_body = {
        "assistant_id": "react",
        "input": {
            "messages": [{"role": "user", "content": "Solve: A farmer has 17 sheep. All but 9 die. How many are left?"}]
        },
        "metadata": {
            "x_auth": "Bearer your-api-key",
            "user_id": "user-123",
            "tenant_id": "tenant-123",
            "llm_provider": "anthropic",  # Use Anthropic
            "llm_tier": "pro",  # Use pro tier (Claude Opus 4.5)
            "enable_thinking": True,  # Enable extended thinking
            "thinking_budget": 2048,  # Thinking token budget
        },
    }

    print("POST http://localhost:2024/runs/stream")
    print("Request body:")
    import json
    print(json.dumps(request_body, indent=2))
    print()


async def main():
    """Run all examples."""
    print("\nReAct Agent LLM Configuration Examples")
    print("=" * 60)
    print()

    await example_default_config()
    await example_provider_flash()
    await example_provider_pro()
    await example_specific_model()
    await example_extended_thinking()
    await example_thinking_all_providers()
    await example_http_request()

    print("=" * 60)
    print("Summary: LLM Configuration Options")
    print("=" * 60)
    print()
    print("Available Providers:")
    print("  - anthropic: Claude models")
    print("  - openai: GPT models")
    print("  - gemini: Google Gemini models")
    print()
    print("Available Tiers:")
    print("  - flash: Fast, cost-effective (default)")
    print("  - pro: Advanced capabilities, more expensive")
    print()
    print("Configuration Keys:")
    print("  - llm_provider: Choose provider")
    print("  - llm_tier: Choose tier (pro/flash)")
    print("  - llm_model: Use specific model ID (overrides tier)")
    print("  - enable_thinking: Enable extended thinking/reasoning (default: False)")
    print("  - thinking_budget: Token budget for thinking (min 1024, default 2048)")
    print()
    print("Extended Thinking Support:")
    print("  - Claude (Anthropic): ✓ Full support, thinking visible")
    print("  - Gemini (Google): ✓ Full support, thinking visible")
    print("  - GPT (OpenAI): ⚠ Partial support, thinking not exposed")
    print()


if __name__ == "__main__":
    asyncio.run(main())

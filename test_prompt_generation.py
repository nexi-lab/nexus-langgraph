#!/usr/bin/env python3
"""Test script to visualize the complete system prompt with sample data."""

import asyncio
from langchain_core.runnables import RunnableConfig

# Import the prompt generation function
import sys
sys.path.insert(0, '/Users/jinjingzhou/nexi-lab/nexus-langgraph')
from shared.prompts.react_prompt import get_system_prompt_async


async def test_prompt_generation():
    """Test prompt generation with sample data."""
    print("=" * 80)
    print("TESTING PROMPT GENERATION")
    print("=" * 80)

    # Create sample config with auth and workspace
    config = RunnableConfig(
        metadata={
            "x_auth": "Bearer sk-clear-de_ecb0de6d_57550abd_296360f31f5467096e8c82c0080a6b6a",
            "nexus_server_url": "http://localhost:2026",
            "workspace_path": "/Users/jinjingzhou/nexi-lab"
        }
    )

    print("\n📋 Configuration:")
    print(f"  Server: {config['metadata']['nexus_server_url']}")
    print(f"  Workspace: {config['metadata']['workspace_path']}")
    print(f"  Auth: {config['metadata']['x_auth'][:30]}...")

    # Generate the complete prompt
    print("\n🔄 Generating system prompt...\n")

    try:
        full_prompt = await get_system_prompt_async(config, role="general")

        print("=" * 80)
        print("COMPLETE SYSTEM PROMPT")
        print("=" * 80)
        print()
        print(full_prompt)
        print()
        print("=" * 80)
        print(f"Total prompt length: {len(full_prompt)} characters")
        print("=" * 80)

        # Analyze sections
        print("\n📊 Prompt Analysis:")
        if "<nexus_tools>" in full_prompt:
            print("  ✓ Contains Nexus tools section")
        if "<skills" in full_prompt:
            print("  ✓ Contains skills section")
            # Count skills
            skill_count = full_prompt.count("<skill>")
            print(f"    - Skills found: {skill_count}")
        else:
            print("  ✗ No skills section found")
        if "<workspace_context>" in full_prompt:
            print("  ✓ Contains workspace context")
        else:
            print("  ✗ No workspace context found")

    except Exception as e:
        print(f"❌ Error generating prompt: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_prompt_generation())

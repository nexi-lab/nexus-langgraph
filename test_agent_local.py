#!/usr/bin/env python3
"""Test the react agent locally."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check required keys
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

if not anthropic_key and not openai_key:
    print("⚠️  No LLM API key found!")
    print("   Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env or environment")
    print("   Example: export ANTHROPIC_API_KEY='sk-ant-your-key'")
    exit(1)

print("✅ API keys found")
print(f"   ANTHROPIC_API_KEY: {'set' if anthropic_key else 'not set'}")
print(f"   OPENAI_API_KEY: {'set' if openai_key else 'not set'}")

# Test agent import
print("\n📦 Testing agent import...")
try:
    from agents.react.agent import agent
    print("✅ Agent imported successfully")
    print(f"   Type: {type(agent)}")
except Exception as e:
    print(f"❌ Failed to import agent: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n✅ Agent is ready for testing!")
print("\nTo test with LangGraph dev server:")
print("   langgraph dev")
print("\nOr test programmatically:")
print("   python3 -c \"from agents.react.agent import agent; print(agent)\"")

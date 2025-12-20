# ReAct Agent

General-purpose ReAct agent with Nexus filesystem access.

## Features

- **File Operations**: Search, read, write files on Nexus filesystem
- **Code Execution**: Execute Python and bash in isolated sandboxes (E2B)
- **Web Search**: Search the web and crawl web pages (optional)
- **Memory Access**: Query and retrieve stored memory records
- **Multi-LLM Support**: Works with Claude, GPT-4, or OpenRouter

## Tools Available

### Core Nexus Tools (from nexus-fs-python)
1. `grep_files` - Search file content using regex patterns
2. `glob_files` - Find files by name pattern
3. `read_file` - Read file content
4. `write_file` - Write content to Nexus filesystem
5. `python` - Execute Python code in sandbox
6. `bash` - Execute bash commands in sandbox
7. `query_memories` - Query stored memory records

### Optional Web Tools
8. `web_search` - Search the web (requires TAVILY_API_KEY)
9. `web_crawl` - Fetch web pages as markdown (requires FIRECRAWL_API_KEY)

## Usage

Deploy via LangGraph Platform as `react` assistant.

### Environment Variables

Required:
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` or `OPENROUTER_API_KEY` - LLM provider
- `NEXUS_API_KEY` - Nexus server authentication (or passed via metadata.x_auth)

Optional:
- `NEXUS_SERVER_URL` - Nexus server URL (default: http://localhost:8080)
- `E2B_TEMPLATE_ID` - E2B sandbox template ID
- `TAVILY_API_KEY` - For web search tool
- `FIRECRAWL_API_KEY` - For web crawl tool

### Example Request

```json
{
  "assistant_id": "react",
  "input": {
    "messages": [{"role": "user", "content": "Find all Python files in /workspace"}]
  },
  "metadata": {
    "x_auth": "Bearer sk-your-nexus-api-key",
    "opened_file_path": "/workspace/admin/script.py"
  }
}
```

## Configuration

The agent uses:
- **LLM**: Claude Sonnet 4.5 (default) or configured via environment
- **Tools**: All Nexus tools + optional web tools
- **Prompt**: Dynamic prompt with opened file context


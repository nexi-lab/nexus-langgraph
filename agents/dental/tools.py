"""
Citation retrieval tool for the dental agent.

Uses Tavily API for web search to find relevant dental sources.
"""

import os
from langchain_core.tools import tool
from tavily import TavilyClient


def _search_tavily(query: str) -> list[dict]:
    """
    Search using Tavily API and convert results to citations.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        # Fallback to empty results if no API key
        return []
    
    client = TavilyClient(api_key=api_key)
    
    # Add dental context to the query for better results
    search_query = f"dental dentistry {query}"
    
    try:
        response = client.search(
            query=search_query,
            search_depth="basic",
            max_results=5,
            include_answer=False,
        )
        
        citations = []
        for i, result in enumerate(response.get("results", []), start=1):
            # Extract domain as publication source
            url = result.get("url", "")
            domain = url.split("/")[2] if url and "/" in url else "Web Source"
            
            # Clean up domain name for display
            publication = domain.replace("www.", "").replace(".com", "").replace(".org", "").replace(".gov", "")
            publication = publication.title()
            
            citations.append({
                "id": f"cite-{i}",
                "marker": f"[{i}]",
                "title": result.get("title", "Untitled"),
                "publication": publication,
                "year": 2024,  # Tavily doesn't provide year, use current
                "url": url,
            })
        
        return citations if citations else []
        
    except Exception as e:
        print(f"Tavily search error: {e}")
        return []


@tool
def search_dental_literature(query: str) -> list[dict]:
    """
    Search dental literature and return relevant citations.

    Use this tool when you need to cite sources for dental clinical information.
    Always cite sources when providing treatment recommendations, dosages,
    or clinical guidelines.

    Args:
        query: The dental topic or question to search for

    Returns:
        List of citations with title, publication, year, and marker
    """
    citations_data = _search_tavily(query)
    return citations_data

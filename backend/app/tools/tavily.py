from tavily import TavilyClient
from typing import List, Dict
from ..core.settings import settings
import structlog

logger = structlog.get_logger(__name__)

tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

async def tavily_search(query: str, max_results: int = 8) -> List[Dict]:
    """Search using Tavily"""
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True
        )

        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
                "snippet": item.get("snippet", "")[:400],
                "score": item.get("score", 0.8)
            })

        return results
    
    except Exception as e:
        logger.error("Tavily search failed", error=str(e))
        return []

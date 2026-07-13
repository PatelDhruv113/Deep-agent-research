from langchain_groq  import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import structlog
from typing import Dict, List

from ..core.settings import settings
from ..tools.tavily import tavily_search
from ..tools.arxiv import arxiv_search

logger = structlog.get_logger(__name__)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temprature=0.1,
    api_key=settings.GROQ_API_KEY
)

async def search_sub_question(state: Dict) -> Dict:
    """Individual searcher worker for one sub-questions"""
    query = state.get("query", "")

    logger.info("Searcher executing", query=query[:80])

    try:
        results = await tavily_search(query, max_results=8)

        findings = []
        for result in results:
            findings.append({
                "sub_question":query,
                "content": result.get("content", ""),
                "source": {
                    "url": result.get("url"),
                    "title": result.get("title"),
                    "snippet": result.get("snippet", "")[:300],
                    "tool_name": "tavily"
                }
            })

        return {
            "findings": findings,
            "status": "success"
        }
    
    except Exception as e:
        logger.error("Searcher failed", error=str(e))
        return {
            "findings": [],
            "status": "failed",
            "error": str(e)
        }
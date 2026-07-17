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
    temperature=0.1,
    api_key=settings.GROQ_API_KEY
)

async def search_sub_question(sub_q: Dict, assigned_tools: List[str]) -> List[Dict]:
    """Individual searcher worker for one sub-question"""
    query = sub_q.get("question", "")
    logger.info("Searcher executing", query=query[:80], tools=assigned_tools)

    findings = []
    
    if "tavily" in assigned_tools or not assigned_tools:
        try:
            results = await tavily_search(query, max_results=5)
            for result in results:
                findings.append({
                    "sub_question": query,
                    "content": result.get("content", ""),
                    "source": {
                        "url": result.get("url"),
                        "title": result.get("title"),
                        "snippet": result.get("snippet", "")[:300],
                        "tool_name": "tavily"
                    }
                })
        except Exception as e:
            logger.error("Tavily search failed in searcher", error=str(e))

    if "arxiv" in assigned_tools:
        try:
            results = await arxiv_search(query, max_results=3)
            for result in results:
                findings.append({
                    "sub_question": query,
                    "content": result.get("content", ""),
                    "source": {
                        "url": result.get("url"),
                        "title": result.get("title"),
                        "snippet": result.get("snippet", "")[:300],
                        "tool_name": "arxiv"
                    }
                })
        except Exception as e:
            logger.error("Arxiv search failed in searcher", error=str(e))

    return findings
import arxiv
from typing import List, Dict
import structlog

logger = structlog.get_logger(__name__)

async def arxiv_search(query: str, max_results: int = 5) -> List[Dict]:
    """Search arXiv for academic papers"""
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for result in client.results(search):
            results.append({
                "title": result.title,
                "url": result.entry_id,
                "content": result.summary,
                "snippet": result.summary[:400],
                "score": 0.8
            })
        return results
    except Exception as e:
        logger.error("Arxiv search failed", error=str(e))
        return []

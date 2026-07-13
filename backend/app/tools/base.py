from typing import List, Dict, Any
import structlog
from.tavily import tavily_search

logger = structlog.get_logger(__name__)

class ToolResult:
    """Standardized tool output format"""
    def __init__(self, content: str, source: Dict[str, Any]):
        self.content = content
        self.source = source


async def execute_tool(tool_name: str, query: str) -> List[Dict]:
    """Unified tool executor"""
    logger.info("Executing tool", tool=tool_name, query=query[:100])

    if tool_name == "tavily":
        return await tavily_search(query)

    logger.warning("Tool not implemented", tool=tool_name)
    return []

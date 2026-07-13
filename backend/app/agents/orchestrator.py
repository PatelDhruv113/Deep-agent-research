from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing import List, Dict
import structlog
import uuid


from ..core.settings import settings
from ..tools.base import get_tools_for_type

logger = structlog.get_logger(__name__)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temprature=0.2,
    api_key=settings.GROQ_API_KEY
)

class Delegation(BaseModel):
    sub_question_id: str
    assigned_tools: List[str]
    priority: int

async def orchestrate(state: Dict) -> Dict:
    """Main orchestrator - decides next actions and delegated"""

    sub_questions = state.get("sub_questions", [])
    finding_count = len(state.get("findings", []))

    if not sub_questions:
        return {"status": "error", "error": "No sub questions generated"}
    

    pending_questions = [q for q in sub_questions if q.get("status" != "done")]

    if not pending_questions:
        return {"status": "ready_for_critic"}

    delegation = []
    for q in pending_questions[:4]:
        tool_set = get_tools_for_type(q.get("type", "general"))
        delegation.append({
            "sub_question_id": q["id"],
            "assigned_tools": tool_set,
            "priority": q.get("priority", 1)
        })

    logger.info("Orchestrate delegated",
        pending=len(pending_questions),
        delegated=len(delegation)
    )

    return {
        "delegations": delegations,
        "status": "researching"
    }

def get_tools_for_type(qtype: str) -> List[str]:
    """Route tools based on question type"""
    if qtype == "academic":
        return ["arxiv", "tavily"]
    elif qtype == "technical":
        return ["tavily"]
    else:
        return ["tavily"]




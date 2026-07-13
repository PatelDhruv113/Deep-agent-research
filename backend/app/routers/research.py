from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
import structlog

from ..graph.workflow import run_research
from ..core.settings import settings

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["research"])

class ResearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class ResearchResponse(BaseModel):
    session_id: str
    status: str
    message: str
    final_report: Optional[str] = None

@router.post("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a deep research session"""

    session_id = str(uuid.uuid4())

    logger.info("New research request received", session_id=session_id, query=request.query[:100])

    try:
        background_tasks.add_task(
            run_background_research,
            request.query,
            session_id,
            request.user_id
        )

        return ResearchResponse(
            session_id=session_id,
            status="started",
            message="Research session started. This may take 30-90 seconds."
        )
    except Exception as e:
        logger.error("Failed to start research", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start research")
    
async def run_background_research(query: str, session_id: str, user_id: Optional[str]=None):
    """Background task to run the full agent swarm"""
    try:
        result = await run_research(query, session_id)

        logger.info("Research completed", 
                    session_id=session_id,
                    total_agents=result.get("agent_invocations", 0),
                    cost=result.get("total_cost", 0)
                    )
    except Exception as e:
        logger.error("Research Failed", session_id=session_id, error=str(e))

@router.get("/research/{session_id}")
async def get_research_status(session_id: str):
    """Get status of a research session"""

    return {"session_id": session_id, "status": "in_progress"}
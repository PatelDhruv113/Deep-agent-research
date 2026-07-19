from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class Source(BaseModel):
    source_id: str
    url: str
    title: str
    snippet: str
    full_content: Optional[str] = None
    published_date: Optional[str] = None
    domain_authority: float =  50.0
    tool_name: str

class Claim(BaseModel):
    claim: str
    sources: List[Source]
    trust_score: int
    reasoning: Optional[str] = None

class ResearchState(TypedDict):
    """Shared state for the entire LangGraph workflow"""

    research_session_id: str
    query: str
    user_id: Optional[str] = None

    plan: Optional[Dict] = None
    sub_questions: List[Dict]
    delegations: Optional[List[Dict]] = None
    critic_feedback: Optional[str] = None
    needs_more_research: Optional[bool] = None

    findings: List[Dict] = None
    verified_claims: List[Claim]
    rejected_claims: List[Dict]

    current_round: int = 0
    critic_rounds: int = 0
    total_cost: float = 0.0
    agent_invocations: int = 0
    findings_invocations: int = 0

    status: str = "in_progress"
    active_node: Optional[str] = None
    final_report: Optional[str] = None
    error: Optional[str] = None

State = ResearchState
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import List, Dict
import structlog
import uuid


from ..core.settings import settings
from ..tools.base import get_tools_for_type

logger = structlog.get_logger(__name__)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=settings.GROQ_API_KEY
)

class Delegation(BaseModel):
    sub_question_id: str
    assigned_tools: List[str]
    priority: int

async def orchestrate(state: Dict) -> Dict:
    """Main orchestrator - decides next actions and delegates"""

    sub_questions = list(state.get("sub_questions", []))
    finding_count = len(state.get("findings", []))

    if not sub_questions:
        return {"status": "error", "error": "No sub questions generated"}

    pending_questions = [q for q in sub_questions if q.get("status") != "done"]

    if not pending_questions and state.get("critic_feedback") and state.get("critic_rounds", 0) < settings.MAX_CRITIC_ROUNDS:
        logger.info("Generating follow-up sub-questions based on critic feedback")
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an orchestrator. Based on the original query and the critic's feedback on previous findings, generate 2-3 new targeted sub-questions to address the gaps or weak sources.
                Classify each question's type: academic (for papers/formal science), current_events, technical, or general."""),
                ("user", "Original Query: {query}\n\nCritic Feedback: {feedback}")
            ])
            
            class NewSubQuestion(BaseModel):
                question: str
                type: str = Field(..., description="academic | current_events | technical | general")
                priority: int
            
            class NewSubQuestions(BaseModel):
                sub_questions: List[NewSubQuestion]

            structured_llm = llm.with_structured_output(NewSubQuestions)
            new_qs_resp = await structured_llm.ainvoke(
                prompt.format_messages(query=state.get("query"), feedback=state.get("critic_feedback"))
            )
            
            new_sub_questions = []
            start_idx = len(sub_questions) + 1
            for i, q in enumerate(new_qs_resp.sub_questions):
                new_sub_questions.append({
                    "id": f"q{start_idx + i}",
                    "question": q.question,
                    "type": q.type,
                    "priority": q.priority,
                    "status": "pending"
                })
            
            sub_questions.extend(new_sub_questions)
            pending_questions = new_sub_questions
            logger.info("Added follow-up sub-questions", count=len(new_sub_questions))
        except Exception as e:
            logger.error("Failed to generate follow-up questions", error=str(e))

    if not pending_questions:
        return {
            "status": "ready_for_critic",
            "sub_questions": sub_questions
        }

    delegations = []
    for q in pending_questions[:4]:
        tool_set = get_tools_for_type(q.get("type", "general"))
        delegations.append({
            "sub_question_id": q["id"],
            "assigned_tools": tool_set,
            "priority": q.get("priority", 1)
        })

    logger.info("Orchestrate delegated",
        pending=len(pending_questions),
        delegated=len(delegations)
    )

    return {
        "delegations": delegations,
        "sub_questions": sub_questions,
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




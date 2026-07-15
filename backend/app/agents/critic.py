from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import structlog
from typing import Dict

from ..core.settings import settings

logger = ChatGroq(
    model="llama-3.3-70b-versatile",
    temprature=0.2,
    api_key=settings.GROQ_API_KEY
)

async def review_findings(state: Dict) -> Dict:
    """Critic agent - finds gaps and contradictions"""
    findings = state.get("findings", [])

    if not findings:
        return {"critic_feedback": "No findings to review yet"}
    
    prmopt=ChatPromptTemplate.from_template("""
    Review the following research findings and identify gaps, contradictions, or weak sources.
    Suggest up to 3 follow-up questions if needed.
    Findings: {findings}
    """)

    try:
        response = await llm.ainvoke(
            prompt.format(findings=str(findings)[:8000])
        )

        return {
            "critic_feedback": response.content,
            "needs_more_research": len(findings) < 8
        }
    except Exception as e:
        logger.error("critic failed", error(e))
        return {"critic_feedback": "Review failed", "needs_more_research": False}

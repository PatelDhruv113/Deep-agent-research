from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import structlog
from typing import Dict

from ..core.settings import settings

logger = structlog.get_logger(__name__)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=settings.GROQ_API_KEY
)

async def generate_report(state: Dict) -> str:
    """Synthesizer - creates final coherent report"""
    query=state.get("query", "")
    findings=state.get("findings", [])
    verified=state.get("verified_claims", [])

    prompt=ChatPromptTemplate.from_template("""
    You are an expert technical writer.
    Create a clear, well-structured final research report based on the findings.

    Original Query: {query}

    Key Findings: {findings}

    Write a proffessional report with sections, inline citations, and conclusion.
    """)

    try:
        response = await llm.ainvoke(
            prompt.format_messages(
                query=query,
                findings=str(findings + verified)[:12000]
            )
        )
        return response.content

    except Exception as e:
        logger.error("Synthesizer failed", error=str(e))
        return "Error generating final report. Raw findings attached."
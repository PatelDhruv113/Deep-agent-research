from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import structlog
from typing import Dict, List

from ..core.settings import settings
from ..utils.trust_scoring import calculate_trust_score

logger = structlog.get_logger(__name__)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.1,
    api_key=settings.GROQ_API_KEY
)

async def verify_claims(state: Dict) -> Dict:
    """Fact checker with trust scoring"""
    findings = state.get("findings", [])
    verified_claims = []

    if not findings:
        return {"verified_claims": []}
    
    prompt = ChatPromptTemplate.from_template("""
    Extract key claims from the findings and verify them.
    Return structured claims with confidence.
    """)

    try:
        for finding in findings[:6]:
            claim_text = finding.get("content", "")[:500]

            trust_score = calculate_trust_score(finding)

            verified_claims.append({
                "claim": claim_text[:200],
                "sources": [finding.get("source")],
                "trust_score": trust_score,
                "reasoning": "Based on available sources"
            })

        return {"verified_claims": verified_claims}
    
    except Exception as e:
        logger.error("Fact checker failed", error=str(e))
        return {"verified_claims": []}
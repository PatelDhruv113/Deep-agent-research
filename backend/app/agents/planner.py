from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field 
from typing import List, Dict
import structlog 

from ..core.settings import settings

logger = structlog.get_logger(__name__)

class SubQuestion(BaseModel):
    id: str
    question: str 
    type: str = Field(..., description="academic | current_events | technical | general")
    priority: int 

class ResearchPlan(BaseModel):
    hypothesis: str
    key_entities: List[str]
    sub_questions: List[SubQuestion]
    search_strategy: str

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temprature=0.3,
    api_key=settings.GROQ_API_KEY
)

async def generate_plan(query: str) -> Dict:
    """Generate strcutred research plan"""
    prompt=ChatPromptTemplate.from_messages([
        ("system", """You are an expert research planner.
        Break down the user query into 4-8 smart sub-questions.
        Focus on logical decomposition and diverse angles."""),
        ("user", "{query}")
    ])

    structured_llm = llm.with_structured_output(ResearchPlan)

    try:
        plan = await structured_llm.ainvoke(
            prompt.format_message(query=query)
        )

        logger.info("Research plan generated", sub_questions=len(plan,sub_questions))

        return plan.model_dump()
    
    except Exception as e:
        logger.error("Planner failed", error=str(e))

        return {
            "hypothesis": "Direct research on the query",
            "key-entities": [],
            "sub_questions": [
                {"id": "q1", "questions": query, "type": "general", "priority": 1}
            ],
            "search_strategy": "Basic web search"
        }
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Union
import structlog

from ..core.settings import settings

logger = structlog.get_logger(__name__)

class SubQuestion(BaseModel):
    id: str
    question: str 
    type: str = Field(..., description="academic | current_events | technical | general")
    priority: Union[int, str] = Field(..., description="1-5 priority rank (1 is highest)")

    @field_validator('priority', mode='before')
    @classmethod
    def coerce_priority(cls, v):
        try:
            return int(v)
        except (ValueError, TypeError):
            return 1

class ResearchPlan(BaseModel):
    sub_questions: List[SubQuestion]
    search_strategy: str

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
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
            prompt.format_messages(query=query)
        )

        logger.info("Research plan generated", sub_questions=len(plan.sub_questions))

        return plan.model_dump()
    
    except Exception as e:
        logger.error("Planner failed", error=str(e))

        return {
            "hypothesis": "Direct research on the query",
            "key-entities": [],
            "sub_questions": [
                {"id": "q1", "question": query, "type": "general", "priority": 1}
            ],
            "search_strategy": "Basic web search"
        }
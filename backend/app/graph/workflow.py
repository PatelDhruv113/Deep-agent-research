from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import structlog

from .state import ResearchState
from .nodes import (
    planner_node,
    orchestrator_node,
    searcher_node,
    critic_node,
    fact_checker_node,
    synthesizer_node,
    should_continue_research
)

logger = structlog.get_logger(__name__)

def create_research_graph():
    """Build the complete multi-agent research workflow"""

    workflow = StateGraph(ResearchState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("searcher", searcher_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("fast_checker", fact_checker_node)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.set_entry_point("planner")
    
    workflow.add_edge("planner", "orchestrator")

    workflow.add_conditional_edges(
        "orchestrator",
        should_continue_research,
        {
            "searcher": "searcher",
            "synthesize": "fast_checker"
        }
    )

    workflow.add_edge("searcher", "critic")
    workflow.add_edge("critic", "orchestrator")
    workflow.add_edge("fast_checker", "synthesizer")
    workflow.add_edge("synthesizer", END)

    memory = MemorySaver()

    app = workflow.compile(checkpointer=memory)
    return app

research_graph = create_research_graph()

async def run_research(query: str, session_id: str):
    """Main entry point to run research"""
    initial_state: ResearchState = {
        "research_session_id": session_id,
        "query": query,
        "sub_questions": [],
        "findings": [],
        "verified_claims" : [],
        "rejected_claims" : [],
        "status" : "in_progress",
        "current_round" : 0,
        "critic_rounds": 0,
        "total_cost": 0.0,
        "agent_invocations": 0,
        "findings_invocations": 0
    }

    logger.info("Starting research session", session_id=session_id, query=query)

    result = await research_graph.ainvoke(
        initial_state,config = {
            "configurable": {
                "thread_id": session_id
            }
        }
    )

    return result
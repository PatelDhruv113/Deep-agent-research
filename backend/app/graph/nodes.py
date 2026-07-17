from langgraph.graph import StateGraph
from typing import Dict, Any
import structlog
from datetime import datetime
import asyncio

from ..core.settings import settings
from .state import ResearchState
from ..agents import(
    planner,
    orchestrator,
    searcher,
    critic,
    fact_checker,
    synthesizer
)

logger = structlog.get_logger(__name__)

async def planner_node(state: ResearchState) -> ResearchState:
    """Generate research plan and sub-questions"""
    logger.info("Planner agent started", query=state["query"])

    plan = await planner.generate_plan(state["query"])

    state["plan"] = plan
    state["sub_questions"]=plan.get("sub_questions", [])
    state["agent_invocations"] += 1
    return state

async def orchestrator_node(state: ResearchState) -> ResearchState:
    """Main orchestrator - delegates to searcher"""
    logger.info("Orchestrator started", sub_questions=len(state.get("sub_questions", [])))

    result = await orchestrator.orchestrate(state)
    state.update(result)
    state["agent_invocations"] += 1
    return state

async def searcher_node(state: ResearchState) -> ResearchState:
    """Parallel searcher for sub-questions"""
    logger.info("Searcher working on sub-questions")

    delegations = state.get("delegations", [])
    sub_questions = state.get("sub_questions", [])

    tasks = []
    delegated_qs = []

    for delegation in delegations:
        sub_q_id = delegation.get("sub_question_id")
        sub_q = next((q for q in sub_questions if q.get("id") == sub_q_id), None)
        if sub_q:
            delegated_qs.append(sub_q)
            tasks.append(
                searcher.search_sub_question(sub_q, delegation.get("assigned_tools", ["tavily"]))
            )

    if tasks:
        results = await asyncio.gather(*tasks)
        all_findings = [finding for sublist in results for finding in sublist]

        if state.get("findings") is None:
            state["findings"] = []
        state["findings"].extend(all_findings)

        for sub_q in delegated_qs:
            sub_q["status"] = "done"

    state["findings_invocations"] += 1
    state["agent_invocations"] += 1
    return state

async def critic_node(state:ResearchState) -> ResearchState:
    """Quality control -finds gaps"""
    logger.info("Critic agent reviewing findings")

    result  = await critic.review_findings(state)
    state.update(result)
    state["critic_rounds"] += 1
    state["agent_invocations"] += 1
    return state

async def fact_checker_node(state: ResearchState) -> ResearchState:
    """Verify claims with trust scoring"""
    logger.info("Fast Checker started")

    result = await fact_checker.verify_claims(state)
    state.update(result)
    state["agent_invocations"] += 1
    return state

async def synthesizer_node(state: ResearchState) -> ResearchState:
    """Generate final report"""
    logger.info("Synhesizer creating final report")

    report = await synthesizer.generate_report(state)
    state["final_report"] = report
    state["status"] = "completed"
    state["agent_invocations"] += 1
    return state

def should_continue_research(state: ResearchState) -> str:
    """Decide whether to continue research or synthesize"""
    if state.get("critic_rounds", 0) >= settings.MAX_CRITIC_ROUNDS:
        return "synthesize"
    
    status = state.get("status")
    if status == "researching":
        return "searcher"
        
    return "synthesize" 
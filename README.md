# Deep Research Agent Swarm

Production-grade multi-agent research system built with **LangGraph**, **Groq**, and **Gemini**.

An open-source implementation of advanced agentic research patterns used by Anthropic, OpenAI Deep Research, and Perplexity.

## Features

- **Hierarchical Agent Swarm** (Planner → Orchestrator → Searchers → Critic → Synthesizer)
- **Trust Scoring System** with source verification
- **LangGraph** with cycles, checkpointing, and parallel execution
- **Cost Control** & hard safety limits
- **Real-time capable** architecture
- Groq + Gemini optimized (low cost)

## Tech Stack

- **Backend**: FastAPI, LangGraph, LangChain
- **LLMs**: Groq (Llama 3.3 70B), Gemini
- **Search**: Tavily, Arxiv
- **Observability**: Structlog + Langfuse ready
- **Deployment**: Docker, Railway / Fly.io ready

## Quick Start

```bash
cd backend
uv venv
uv sync
cp .env.example .env
# Add your GROQ_API_KEY and TAVILY_API_KEY
uv run uvicorn app.main:app --reload
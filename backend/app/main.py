from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog
from contextlib import asynccontextmanager
from .core.settings import settings
from .middleware.logging_middleware import LoggingMiddleware
from .routers.research import router as research_router
from .core.config import logger

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Deep Research Agent Swarm", environment=settings.ENVIRONMENT)
    yield
    logger.info("Shutting down Deep Research Agent Swarm")

app = FastAPI(
    title="Deep Research Agent Swarm",
    description="Production-grade Multi-Agent Research System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(LoggingMiddleware)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    return  {
        "message": "Deep Research Agent Swarm API is running",
        "docs": "/docs"
    }

app.include_router(research_router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

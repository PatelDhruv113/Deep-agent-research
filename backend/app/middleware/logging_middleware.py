from fastapi import Request, Response
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        logger.info("Request started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None
        )

        response = await call_next(request)

        process_time =  (time.time() - start_time) * 1000
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(process_time, 2)
        )

        return response
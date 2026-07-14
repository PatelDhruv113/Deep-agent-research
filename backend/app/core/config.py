from .settings import settings
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory = structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger(__name__)

def get_settings():
    return settings

logger.info("Application configuration loaded",
    environment=settings.ENVIRONMENT,
    debug = settings.DEBUG
)
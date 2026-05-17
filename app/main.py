import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from app.config import get_settings
from app.logging_config import configure_logging
from app.routers import health, tasks
from app.schemas import RootResponse

settings = get_settings()
configure_logging(settings.log_level)

logger = logging.getLogger(__name__)

if settings.startup_delay_seconds > 0:
    logger.info("Startup delay enabled: %s seconds", settings.startup_delay_seconds)
    time.sleep(settings.startup_delay_seconds)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="A small API for DevOps internship practice.",
)


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)

    logger.info(
        "%s %s -> %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response


@app.get("/", response_model=RootResponse, tags=["root"])
def root() -> RootResponse:
    return RootResponse(
        service=settings.app_name,
        environment=settings.app_env,
        docs="/docs",
        health={
            "live": "/health/live",
            "ready": "/health/ready",
        },
    )


app.include_router(health.router)
app.include_router(tasks.router)

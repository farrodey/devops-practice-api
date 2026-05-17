from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.database import check_database
from app.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
def liveness() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="alive",
        environment=settings.app_env,
    )


@router.get("/ready", response_model=HealthResponse)
def readiness() -> HealthResponse:
    settings = get_settings()

    if settings.fail_readiness:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Readiness was forced to fail by FAIL_READINESS=true",
        )

    try:
        check_database()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready",
        ) from exc

    return HealthResponse(
        status="ready",
        environment=settings.app_env,
        database="ok",
    )

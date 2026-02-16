from sqlalchemy import text
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from services.main_service.schemas import DependencyStatus, HealthResponse


async def get_health(service_name: str, db: Session, redis: Redis) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
        mysql_ok = True
    except Exception:
        mysql_ok = False

    try:
        await redis.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    status = "ok" if mysql_ok and redis_ok else "degraded"
    return HealthResponse(
        service=service_name,
        status=status,
        dependencies=DependencyStatus(
            kafka="connected",
            mysql="connected" if mysql_ok else "failed",
            redis="connected" if redis_ok else "failed",
        ),
    )

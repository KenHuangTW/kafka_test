from fastapi import APIRouter

from services.main_service.controller import get_health
from services.main_service.depend import DBSessionDep, RedisDep
from services.main_service.schemas import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health(db: DBSessionDep, redis: RedisDep) -> HealthResponse:
    return await get_health(service_name="main", db=db, redis=redis)

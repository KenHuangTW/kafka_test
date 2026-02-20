from fastapi import APIRouter

from services.payment_service.controller.health_controller import get_health
from services.payment_service.schemas import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return await get_health(service_name="payment")

from services.payment_service.schemas import HealthResponse


async def get_health(service_name: str) -> HealthResponse:
    return HealthResponse(service=service_name, status="ok")

from fastapi import APIRouter

from .event_router import router as event_router
from .health_router import router as health_router
from .payment_router import router as payment_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(event_router)
api_router.include_router(payment_router)

__all__ = ["api_router"]

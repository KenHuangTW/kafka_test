from fastapi import APIRouter

from .event_router import router as event_router
from .health_router import router as health_router
from .member_router import router as member_router
from .product_router import router as product_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(event_router)
api_router.include_router(member_router)
api_router.include_router(product_router)

__all__ = ["api_router"]

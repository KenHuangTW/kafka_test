from fastapi import APIRouter

from .order_router import router as order_router
from .product_router import router as product_router

api_router = APIRouter()
api_router.include_router(product_router)
api_router.include_router(order_router)

__all__ = ["api_router"]

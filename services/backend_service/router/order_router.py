from fastapi import APIRouter

from services.backend_service.controller.order_controller import get_order
from services.backend_service.depend import DBSessionDep
from services.backend_service.schemas import OrderData

router = APIRouter(prefix="/order", tags=["order"])


@router.get("/{order_id}", response_model=OrderData)
async def get_order_by_id(order_id: int, db: DBSessionDep) -> OrderData:
    return await get_order(db=db, order_id=order_id)

from fastapi import APIRouter, Query

from services.backend_service.controller.order_controller import get_order, get_order_list
from services.backend_service.depend import DBSessionDep
from services.backend_service.schemas import OrderGetResponse, OrderListResponse

router = APIRouter(prefix="/order", tags=["order"])


@router.get("/", response_model=OrderListResponse)
async def get_orders(
    db: DBSessionDep,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> OrderListResponse:
    return await get_order_list(db=db, limit=limit, offset=offset)


@router.get("/{order_id}", response_model=OrderGetResponse)
async def get_order_by_id(
    order_id: int,
    db: DBSessionDep,
) -> OrderGetResponse:
    return await get_order(db=db, order_id=order_id)

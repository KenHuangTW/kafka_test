from fastapi import APIRouter, Request

from common.kafka_client import KafkaManager
from services.payment_service.controller.payment_controller import checkout_payment
from services.payment_service.depend import DBSessionDep
from services.payment_service.schemas import PaymentCheckoutRequest, PaymentCheckoutResponse

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/checkout", response_model=PaymentCheckoutResponse)
async def checkout(request: Request, payload: PaymentCheckoutRequest, db: DBSessionDep) -> PaymentCheckoutResponse:
    kafka: KafkaManager = request.app.state.kafka
    return await checkout_payment(db=db, payload=payload, kafka=kafka)

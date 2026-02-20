from fastapi import APIRouter, Request

from common.kafka_client import KafkaManager
from services.payment_service.controller.event_controller import publish_event
from services.payment_service.schemas import EventPublishRequest, EventPublishResponse

router = APIRouter(tags=["events"])


@router.post("/events", response_model=EventPublishResponse)
async def create_event(request: Request, payload: EventPublishRequest) -> EventPublishResponse:
    kafka: KafkaManager = request.app.state.kafka
    return await publish_event(kafka=kafka, payload=payload)

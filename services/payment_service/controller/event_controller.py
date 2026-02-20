import os
from datetime import UTC, datetime
from uuid import uuid4

from common.kafka_client import KafkaManager
from services.payment_service.schemas import EventPublishRequest, EventPublishResponse


async def publish_event(kafka: KafkaManager, payload: EventPublishRequest) -> EventPublishResponse:
    event = {
        "event_id": str(uuid4()),
        "event_type": payload.event_type,
        "entity": payload.entity,
        "entity_id": payload.entity_id,
        "version": payload.version,
        "updated_at": datetime.now(UTC).isoformat(),
        "trace_id": str(uuid4()),
    }
    await kafka.publish(event)
    return EventPublishResponse(status="published", topic=os.getenv("KAFKA_TOPIC", "service.events"))

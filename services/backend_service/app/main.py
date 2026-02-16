import os
from contextlib import asynccontextmanager
from datetime import datetime, UTC
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from common.kafka_client import KafkaManager

SERVICE_NAME = "backend"
kafka = KafkaManager(service_name=SERVICE_NAME)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await kafka.start()

    async def handler(event: dict[str, object]) -> None:
        if event.get("source_service") == SERVICE_NAME:
            return
        print(f"[{SERVICE_NAME}] received event: {event}")

    await kafka.consume_forever(handler)
    yield
    await kafka.stop()


app = FastAPI(title="Backend Service", lifespan=lifespan)


class EventIn(BaseModel):
    event_type: str
    entity: str
    entity_id: str
    version: int


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "ok"}


@app.post("/events")
async def publish_event(payload: EventIn) -> dict[str, str]:
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
    return {"status": "published", "topic": os.getenv("KAFKA_TOPIC", "service.events")}

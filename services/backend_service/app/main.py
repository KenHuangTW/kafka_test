import os
from contextlib import asynccontextmanager
from datetime import datetime, UTC
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from common.kafka_client import KafkaManager
from services.backend_service.controller.cache_event_controller import handle_cache_event
from services.backend_service.database import close_redis
from services.backend_service.router import api_router

SERVICE_NAME = "backend"
kafka = KafkaManager(service_name=SERVICE_NAME)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await kafka.start()

    async def handler(event: dict[str, object]) -> None:
        if event.get("source_service") == SERVICE_NAME:
            return
        await handle_cache_event(event)

    await kafka.consume_forever(handler)
    yield
    await kafka.stop()
    await close_redis()


app = FastAPI(
    title="Backend Service",
    lifespan=lifespan,
    docs_url=f"/{SERVICE_NAME}/docs",
    openapi_url=f"/{SERVICE_NAME}/openapi.json",
)
app.include_router(api_router)


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

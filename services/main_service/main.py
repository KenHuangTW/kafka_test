from contextlib import asynccontextmanager

from fastapi import FastAPI

from common.kafka_client import KafkaManager
from services.main_service.database import close_redis
from services.main_service.router import api_router

SERVICE_NAME = "main"
kafka = KafkaManager(service_name=SERVICE_NAME)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.kafka = kafka
    app.state.service_name = SERVICE_NAME

    await kafka.start()

    async def handler(event: dict[str, object]) -> None:
        if event.get("source_service") == SERVICE_NAME:
            return
        print(f"[{SERVICE_NAME}] received event: {event}")

    await kafka.consume_forever(handler)
    yield
    await kafka.stop()
    await close_redis()


app = FastAPI(title="Main Service", lifespan=lifespan)
app.include_router(api_router)

from contextlib import asynccontextmanager

from common.kafka_client import KafkaManager
from fastapi import FastAPI
from services.payment_service.router import api_router

SERVICE_NAME = "payment"
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


app = FastAPI(
    title="Payment Service",
    lifespan=lifespan,
    docs_url=f"/{SERVICE_NAME}/docs",
    openapi_url=f"/{SERVICE_NAME}/openapi.json",
)
app.include_router(api_router)

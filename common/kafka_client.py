import asyncio
import json
import os
import signal
from contextlib import suppress
from typing import Awaitable, Callable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

JSONDict = dict[str, object]


class KafkaManager:
    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.topic = os.getenv("KAFKA_TOPIC", "service.events")
        self.group_id = os.getenv("KAFKA_GROUP_ID", f"{service_name}-group")
        self._producer: AIOKafkaProducer | None = None
        self._consumer: AIOKafkaConsumer | None = None
        self._consumer_task: asyncio.Task | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._producer.start()

    async def stop(self) -> None:
        if self._consumer_task:
            self._consumer_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._consumer_task

        if self._consumer:
            await self._consumer.stop()

        if self._producer:
            await self._producer.stop()

    async def publish(self, event: JSONDict) -> None:
        if not self._producer:
            raise RuntimeError("Kafka producer has not started")

        payload = {
            "source_service": self.service_name,
            **event,
        }
        await self._producer.send_and_wait(self.topic, payload)

    async def consume_forever(
        self, handler: Callable[[JSONDict], Awaitable[None]]
    ) -> None:
        self._consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await self._consumer.start()

        async def _loop() -> None:
            assert self._consumer is not None
            async for message in self._consumer:
                await handler(message.value)

        self._consumer_task = asyncio.create_task(_loop())


def install_signal_handlers(shutdown_callback: Callable[[], None]) -> None:
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: shutdown_callback())

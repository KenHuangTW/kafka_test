from __future__ import annotations

import os
from typing import Any

from redis.asyncio import Redis

from services.backend_service.database import get_redis


EventPayload = dict[str, object]

ORDER_DETAIL_CACHE_PREFIX = "backend:function:order"
ORDER_LIST_CACHE_PATTERN = "backend:function:order:list:*"
ORDER_UPDATE_COUNTER_KEY = "backend:cache:order:update-counter"

PRODUCT_DETAIL_CACHE_PREFIX = "backend:function:product"
PRODUCT_LIST_CACHE_PATTERN = "backend:function:product:list:*"

EVENT_DEDUP_KEY_PREFIX = "backend:cache:event:processed"

DEFAULT_ORDER_REFRESH_THRESHOLD = 1
DEFAULT_ORDER_REFRESH_WINDOW_SECONDS = 30
DEFAULT_EVENT_DEDUP_TTL_SECONDS = 300


def _int_env(name: str, default: int, *, minimum: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    if value < minimum:
        return default
    return value


def _parse_entity_id(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value))
    except ValueError:
        return None


async def _delete_keys_by_pattern(redis: Redis, pattern: str) -> None:
    batch: list[str] = []
    async for key in redis.scan_iter(match=pattern, count=200):
        batch.append(str(key))
        if len(batch) >= 200:
            await redis.delete(*batch)
            batch.clear()

    if batch:
        await redis.delete(*batch)


async def _invalidate_detail_key(redis: Redis, prefix: str, entity_id: int | None) -> None:
    if entity_id is None:
        return
    await redis.delete(f"{prefix}:{entity_id}")


async def _is_duplicate_event(redis: Redis, event_id: str, dedupe_ttl_seconds: int) -> bool:
    key = f"{EVENT_DEDUP_KEY_PREFIX}:{event_id}"
    created = await redis.set(key, "1", ex=dedupe_ttl_seconds, nx=True)
    return not bool(created)


async def _should_refresh_order_list_cache(
    redis: Redis,
    *,
    threshold: int,
    window_seconds: int,
) -> bool:
    count = await redis.incr(ORDER_UPDATE_COUNTER_KEY)
    if count == 1:
        await redis.expire(ORDER_UPDATE_COUNTER_KEY, window_seconds)
    if count < threshold:
        return False

    await redis.delete(ORDER_UPDATE_COUNTER_KEY)
    return True


async def handle_cache_event(
    event: EventPayload,
    redis_client: Redis | Any | None = None,
    *,
    order_refresh_threshold: int | None = None,
    order_refresh_window_seconds: int | None = None,
    dedupe_ttl_seconds: int | None = None,
) -> None:
    redis = redis_client or get_redis()

    entity = str(event.get("entity", "")).strip().lower()
    if entity not in {"order", "product"}:
        return

    threshold = order_refresh_threshold or _int_env(
        "ORDER_CACHE_REFRESH_THRESHOLD",
        DEFAULT_ORDER_REFRESH_THRESHOLD,
    )
    window_seconds = order_refresh_window_seconds or _int_env(
        "ORDER_CACHE_REFRESH_WINDOW_SECONDS",
        DEFAULT_ORDER_REFRESH_WINDOW_SECONDS,
    )
    dedupe_ttl = dedupe_ttl_seconds or _int_env(
        "CACHE_EVENT_DEDUP_TTL_SECONDS",
        DEFAULT_EVENT_DEDUP_TTL_SECONDS,
    )

    try:
        event_id_raw = event.get("event_id")
        event_id = str(event_id_raw).strip() if event_id_raw is not None else ""
        if event_id and await _is_duplicate_event(redis, event_id, dedupe_ttl):
            return

        entity_id = _parse_entity_id(event.get("entity_id"))

        if entity == "order":
            await _invalidate_detail_key(redis, ORDER_DETAIL_CACHE_PREFIX, entity_id)
            should_refresh_list = await _should_refresh_order_list_cache(
                redis,
                threshold=threshold,
                window_seconds=window_seconds,
            )
            if should_refresh_list:
                await _delete_keys_by_pattern(redis, ORDER_LIST_CACHE_PATTERN)
            return

        await _invalidate_detail_key(redis, PRODUCT_DETAIL_CACHE_PREFIX, entity_id)
        await _delete_keys_by_pattern(redis, PRODUCT_LIST_CACHE_PATTERN)
    except Exception:
        # Cache updates should not stop Kafka consumption.
        return

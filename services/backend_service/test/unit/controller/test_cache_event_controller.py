from __future__ import annotations

from fnmatch import fnmatch

import pytest

from services.backend_service.controller.cache_event_controller import (
    ORDER_UPDATE_COUNTER_KEY,
    handle_cache_event,
)


class FakeRedis:
    def __init__(self, initial: dict[str, str] | None = None) -> None:
        self.store: dict[str, str] = dict(initial or {})
        self.expire_calls: list[tuple[str, int]] = []
        self.delete_calls: list[tuple[str, ...]] = []

    async def delete(self, *keys: str) -> int:
        self.delete_calls.append(tuple(keys))
        deleted = 0
        for key in keys:
            if key in self.store:
                deleted += 1
                del self.store[key]
        return deleted

    async def set(self, key: str, value: str, ex: int | None = None, nx: bool = False) -> bool | None:
        if nx and key in self.store:
            return None
        self.store[key] = value
        return True

    async def incr(self, key: str) -> int:
        value = int(self.store.get(key, "0")) + 1
        self.store[key] = str(value)
        return value

    async def expire(self, key: str, seconds: int) -> bool:
        self.expire_calls.append((key, seconds))
        return True

    async def scan_iter(self, match: str | None = None, count: int | None = None):
        del count
        pattern = match or "*"
        for key in list(self.store.keys()):
            if fnmatch(key, pattern):
                yield key


@pytest.mark.asyncio
async def test_order_events_refresh_list_cache_after_threshold() -> None:
    redis = FakeRedis(
        {
            "backend:function:order:1": "cached-order-1",
            "backend:function:order:2": "cached-order-2",
            "backend:function:order:list:50:0": "cached-order-list-1",
            "backend:function:order:list:10:10": "cached-order-list-2",
        }
    )

    await handle_cache_event(
        {"event_id": "evt-1", "entity": "order", "entity_id": "1"},
        redis_client=redis,
        order_refresh_threshold=2,
        order_refresh_window_seconds=60,
        dedupe_ttl_seconds=600,
    )

    assert "backend:function:order:1" not in redis.store
    assert "backend:function:order:list:50:0" in redis.store
    assert redis.store[ORDER_UPDATE_COUNTER_KEY] == "1"

    await handle_cache_event(
        {"event_id": "evt-2", "entity": "order", "entity_id": "2"},
        redis_client=redis,
        order_refresh_threshold=2,
        order_refresh_window_seconds=60,
        dedupe_ttl_seconds=600,
    )

    assert "backend:function:order:2" not in redis.store
    assert "backend:function:order:list:50:0" not in redis.store
    assert "backend:function:order:list:10:10" not in redis.store
    assert ORDER_UPDATE_COUNTER_KEY not in redis.store


@pytest.mark.asyncio
async def test_duplicate_event_is_ignored() -> None:
    redis = FakeRedis()

    event = {"event_id": "evt-dup", "entity": "order", "entity_id": "9"}
    await handle_cache_event(
        event,
        redis_client=redis,
        order_refresh_threshold=10,
        order_refresh_window_seconds=60,
        dedupe_ttl_seconds=600,
    )
    await handle_cache_event(
        event,
        redis_client=redis,
        order_refresh_threshold=10,
        order_refresh_window_seconds=60,
        dedupe_ttl_seconds=600,
    )

    detail_cache_key = "backend:function:order:9"
    detail_delete_count = sum(key == detail_cache_key for keys in redis.delete_calls for key in keys)
    assert detail_delete_count == 1
    assert redis.store[ORDER_UPDATE_COUNTER_KEY] == "1"


@pytest.mark.asyncio
async def test_product_event_invalidates_product_cache_immediately() -> None:
    redis = FakeRedis(
        {
            "backend:function:product:7": "cached-product",
            "backend:function:product:list:50:0": "cached-product-list",
        }
    )

    await handle_cache_event(
        {"event_id": "evt-product-1", "entity": "product", "entity_id": "7"},
        redis_client=redis,
        order_refresh_threshold=10,
        order_refresh_window_seconds=60,
        dedupe_ttl_seconds=600,
    )

    assert "backend:function:product:7" not in redis.store
    assert "backend:function:product:list:50:0" not in redis.store

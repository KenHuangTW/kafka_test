import pytest

from common.cache_decorator import invalidate_cache_key, redis_api_cache, redis_function_cache


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def get(self, key: str):
        return self.store.get(key)

    async def setex(self, key: str, _ttl: int, value: str) -> None:
        self.store[key] = value

    async def delete(self, key: str) -> None:
        self.store.pop(key, None)


@pytest.mark.asyncio
async def test_function_cache_reads_db_then_hits_redis() -> None:
    redis_client = FakeRedis()
    calls = {"db": 0}

    @redis_function_cache(
        redis_getter=lambda: redis_client,
        ttl_seconds=30,
        prefix="test:function",
        key_builder=lambda args: str(args["product_id"]),
    )
    async def load_product(product_id: int) -> dict[str, int]:
        calls["db"] += 1
        return {"id": product_id}

    first = await load_product(product_id=10)
    second = await load_product(product_id=10)

    assert first == {"id": 10}
    assert second == {"id": 10}
    assert calls["db"] == 1


@pytest.mark.asyncio
async def test_api_cache_miss_then_hit_and_invalidate() -> None:
    redis_client = FakeRedis()
    calls = {"db": 0}

    @redis_api_cache(
        redis_getter=lambda: redis_client,
        ttl_seconds=30,
        prefix="test:api",
        key_builder=lambda args: str(args["product_id"]),
    )
    async def get_product(product_id: int) -> dict[str, int]:
        calls["db"] += 1
        return {"id": product_id}

    await get_product(product_id=7)
    await get_product(product_id=7)
    assert calls["db"] == 1

    await invalidate_cache_key(lambda: redis_client, "test:api:7")
    await get_product(product_id=7)
    assert calls["db"] == 2

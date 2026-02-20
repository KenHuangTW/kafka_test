from __future__ import annotations

import inspect
import json
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any


RedisGetter = Callable[[], Any]
CacheKeyBuilder = Callable[[dict[str, Any]], str]
CacheSerializer = Callable[[Any], str]
CacheDeserializer = Callable[[str], Any]
CachePredicate = Callable[[Any], bool]


def _default_serializer(value: Any) -> str:
    return json.dumps(value)


def _default_deserializer(value: str) -> Any:
    return json.loads(value)


def _default_should_cache(value: Any) -> bool:
    return value is not None


def _build_bound_arguments(func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    signature = inspect.signature(func)
    bound = signature.bind_partial(*args, **kwargs)
    return dict(bound.arguments)


async def invalidate_cache_key(redis_getter: RedisGetter, key: str) -> None:
    try:
        client = redis_getter()
        await client.delete(key)
    except Exception:
        # Cache failure should not break API behavior.
        return


def _redis_cache(
    *,
    redis_getter: RedisGetter,
    ttl_seconds: int,
    prefix: str,
    key_builder: CacheKeyBuilder,
    serializer: CacheSerializer | None = None,
    deserializer: CacheDeserializer | None = None,
    should_cache: CachePredicate | None = None,
):
    serializer_fn = serializer or _default_serializer
    deserializer_fn = deserializer or _default_deserializer
    should_cache_fn = should_cache or _default_should_cache

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound_args = _build_bound_arguments(func, args, kwargs)
            key = f"{prefix}:{key_builder(bound_args)}"

            try:
                client = redis_getter()
                cached_value = await client.get(key)
                if cached_value is not None:
                    return deserializer_fn(cached_value)
            except Exception:
                pass

            value = await func(*args, **kwargs)
            if not should_cache_fn(value):
                return value

            try:
                serialized = serializer_fn(value)
                client = redis_getter()
                await client.setex(key, ttl_seconds, serialized)
            except Exception:
                pass
            return value

        return wrapper

    return decorator


def redis_function_cache(
    *,
    redis_getter: RedisGetter,
    ttl_seconds: int,
    key_builder: CacheKeyBuilder,
    prefix: str = "function-cache",
    serializer: CacheSerializer | None = None,
    deserializer: CacheDeserializer | None = None,
    should_cache: CachePredicate | None = None,
):
    return _redis_cache(
        redis_getter=redis_getter,
        ttl_seconds=ttl_seconds,
        prefix=prefix,
        key_builder=key_builder,
        serializer=serializer,
        deserializer=deserializer,
        should_cache=should_cache,
    )


def redis_api_cache(
    *,
    redis_getter: RedisGetter,
    ttl_seconds: int,
    key_builder: CacheKeyBuilder,
    prefix: str = "api-cache",
    serializer: CacheSerializer | None = None,
    deserializer: CacheDeserializer | None = None,
    should_cache: CachePredicate | None = None,
):
    return _redis_cache(
        redis_getter=redis_getter,
        ttl_seconds=ttl_seconds,
        prefix=prefix,
        key_builder=key_builder,
        serializer=serializer,
        deserializer=deserializer,
        should_cache=should_cache,
    )

import os

from redis.asyncio import Redis


_redis_client: Redis | None = None


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6633"))
        _redis_client = Redis(
            host=host,
            port=port,
            decode_responses=True,
        )
    return _redis_client


async def ping_redis() -> bool:
    try:
        client = get_redis()
        await client.ping()
        return True
    except Exception:
        return False


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None

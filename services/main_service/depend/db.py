from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from services.main_service.database.mysql import get_db_session
from services.main_service.database.redis import get_redis


def get_redis_client() -> Redis:
    return get_redis()


DBSessionDep = Annotated[Session, Depends(get_db_session)]
RedisDep = Annotated[Redis, Depends(get_redis_client)]

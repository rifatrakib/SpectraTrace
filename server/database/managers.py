import json
from functools import lru_cache
from typing import Any, Dict, List, Union

from redis import Redis
from sqlmodel import create_engine

from server.config.factory import settings
from server.models.users import BaseSQLTable as UserTables
from server.utils.messages import raise_410_gone


def create_db_and_tables() -> None:
    if "sqlite" in settings.RDS_URI:
        connect_args = {"check_same_thread": False}
        engine = create_engine(settings.RDS_URI, echo=True, connect_args=connect_args)
    else:
        engine = create_engine(settings.RDS_URI, echo=True)

    UserTables.metadata.create_all(engine)


@lru_cache()
def get_redis_client() -> Redis:
    return Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def ping_redis_server() -> bool:
    client: Redis = get_redis_client()
    return client.ping()


def cache_data(*, key: str, data: Any, ttl: Union[int, None] = None) -> None:
    client: Redis = get_redis_client()
    client.set(key, data, ex=ttl)


def activate_from_cache(*, key: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    try:
        client: Redis = get_redis_client()
        data = json.loads(client.get(key).decode("utf-8"))
        client.delete(key)
        return data
    except Exception:
        raise raise_410_gone(message="Token expired or invalid.")

import json
from time import time
from typing import Any, Dict, List, Tuple, Union

from redis import Redis

from server.database.managers import get_redis_client
from server.events.cache import redis_cache_event
from server.schemas.inc.audit import AuditRequestSchema
from server.utils.messages import raise_410_gone


def cache_data(*, key: str, data: Any, ttl: Union[int, None] = None) -> AuditRequestSchema:
    start_time = time()
    client: Redis = get_redis_client()
    client.set(key, data, ex=ttl)

    return redis_cache_event(
        execution_time=(time() - start_time) * 1000,
        event_method="set",
        event_name="cache-insert",
        event_type="write",
        event_description="Set new data in cache",
        cached_data={key: data},
    )


def is_in_cache(*, key: str) -> Tuple[bool, AuditRequestSchema]:
    start_time = time()
    try:
        client: Redis = get_redis_client()
        is_valid = True if client.exists(key) else False
        if not is_valid:
            return is_valid, None

        event = redis_cache_event(
            execution_time=(time() - start_time) * 1000,
            event_method="exists",
            event_name="cache-check",
            event_type="read",
            event_description="Check if data is in cache",
        )
        return is_valid, event
    except Exception:
        raise raise_410_gone(message="Token expired or invalid.")


def activate_from_cache(
    *,
    key: str,
) -> Tuple[Union[List[Dict[str, Any]], Dict[str, Any]], List[AuditRequestSchema]]:
    events = []
    start_time = time()

    try:
        client: Redis = get_redis_client()
        data = json.loads(client.get(key).decode("utf-8"))
        events.append(
            redis_cache_event(
                execution_time=(time() - start_time) * 1000,
                event_method="get",
                event_name="cache-get",
                event_type="read",
                event_description="Get data from cache",
                cached_data={key: data},
            )
        )

        client.delete(key)
        events.append(
            redis_cache_event(
                execution_time=(time() - start_time) * 1000,
                event_method="delete",
                event_name="cache-delete",
                event_type="write",
                event_description="Delete data from cache",
            )
        )

        return data, events
    except Exception:
        raise raise_410_gone(message="Token expired or invalid.")


def read_from_cache(
    *,
    key: str,
) -> Tuple[Union[List[Dict[str, Any]], Dict[str, Any]], AuditRequestSchema]:
    start_time = time()

    try:
        client: Redis = get_redis_client()
        data = json.loads(client.get(key).decode("utf-8"))

        event = redis_cache_event(
            execution_time=(time() - start_time) * 1000,
            event_method="get",
            event_name="cache-get",
            event_type="read",
            event_description="Get data from cache",
            cached_data={key: data},
        )

        return data, event
    except Exception:
        raise raise_410_gone(message="Token expired or invalid.")

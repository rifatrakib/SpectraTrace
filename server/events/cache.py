from typing import Any, Dict, List, Union

from server.config.factory import settings
from server.events.templates import get_event_template
from server.schemas.common.audit import MetadataSchema
from server.schemas.inc.audit import AuditRequestSchema


def redis_cache_event(
    execution_time: float,
    event_method: str,
    event_name: str,
    event_type: str,
    event_description: str,
    cached_data: Union[Dict[str, Any], None] = None,
    metadata: List[MetadataSchema] = [],
) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("cache-events")

    event_data.method = event_method
    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = event_name
    event_data.event.type = event_type
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.1  # sample value
    event_data.event.memory_usage = 0.1  # sample value
    event_data.event.description = event_description
    event_data.actor.detail = {"agent": "redis", "data": cached_data}
    event_data.resource.detail = {
        "name": "cache",
        "store": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    }
    event_data.metadata = metadata

    return event_data

import json
from typing import List, Union

from server.config.factory import settings
from server.events.templates import get_event_template
from server.models.users import UserAccount
from server.schemas.common.audit import MetadataSchema
from server.schemas.inc.audit import AuditRequestSchema


def relational_db_event(
    execution_time: float,
    affected_resource_count: int,
    user: UserAccount,
    event_method: str,
    event_name: str,
    event_type: str,
    event_description: Union[str, None] = None,
    metadata: List[MetadataSchema] = [],
) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("rdbms-events")

    event_data.method = event_method
    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = event_name
    event_data.event.type = event_type
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = affected_resource_count
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.1  # sample value
    event_data.event.memory_usage = 0.1  # sample value
    event_data.event.description = event_description
    event_data.actor.detail = {
        "agent": "SQLAlchemy",
        "model": "UserAccount",
        "parameters": json.loads(user.json()),
    }
    event_data.resource.detail = {"database": settings.POSTGRES_DB, "table": "accounts"}
    event_data.metadata = metadata

    return event_data

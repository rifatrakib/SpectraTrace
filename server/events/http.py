from typing import List

from fastapi import Request

from server.events.templates import get_event_template
from server.schemas.common.audit import MetadataSchema
from server.schemas.inc.audit import AuditRequestSchema


def create_http_event(
    request: Request,
    status_code: int,
    affected_resource_count: int,
    execution_time: float,
    metadata: List[MetadataSchema] = [],
) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("http-events")

    event_data.method = request.method
    event_data.status = "success" if status_code < 400 else "error"
    event_data.level = "info" if status_code < 400 else "error"
    event_data.event.name = str(request.url)
    event_data.event.type = "http"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = affected_resource_count
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.1  # sample value
    event_data.event.memory_usage = 0.1  # sample value
    event_data.event.description = "Information about HTTP request-response cycle"
    event_data.actor.origin = f"{request.client.host}:{request.client.port}"
    event_data.actor.detail = {"user_agent": request.headers.get("user-agent", "N/A")}
    event_data.resource.id = request.url.path.strip("/").replace("/", "-")
    event_data.resource.name = request.url.path
    event_data.resource.type = "http"
    event_data.metadata = metadata

    return event_data

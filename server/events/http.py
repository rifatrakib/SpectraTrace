import json

from fastapi import Request

from server.models.users import UserAccount
from server.schemas.common.audit import MetadataSchema
from server.schemas.inc.audit import AuditRequestSchema
from server.utils.tasks import publish_task
from server.utils.utilities import get_event_template


def create_http_event(
    request: Request,
    status_code: int,
    affected_resource_count: int,
    execution_time: float,
    admin: UserAccount,
):
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
    event_data.actor.detail = dict(request.headers)
    event_data.resource.id = request.url.path.strip("/").replace("/", "-")
    event_data.resource.name = request.url.path
    event_data.resource.type = "http"
    event_data.metadata = [
        MetadataSchema(
            is_metric=False,
            name="request_headers",
            value=json.dumps(dict(request.headers)),
        ),
    ]

    publish_task(admin=admin, bucket=admin.username, event_data=event_data)

from datetime import datetime
from typing import Any, Dict

from pydantic import Field

from server.schemas.base import BaseResponseSchema
from server.schemas.common.audit import ActorSchema, EventSchema, ResourceSchema, TagSchema


class EventResponseSchema(EventSchema):
    id: str = Field(title="Event ID", description="ID of the event that was performed")


class AuditResponseSchema(BaseResponseSchema):
    category: str = Field(title="Category", description="Category of the event, to be used as measurement in InfluxDB")
    tags: TagSchema = Field(title="Source Information", description="Tags of InfluxDB measurement")
    method: str = Field(title="Method", description="Method that was used to perform the action")
    status: str = Field(title="Status", description="Status of the event that was performed")
    level: str = Field(title="Level", description="Level of the event that was performed")
    event: EventResponseSchema = Field(title="Event", description="Event that was performed")
    actor: ActorSchema = Field(title="Actor", description="Actor that performed the event")
    resource: ResourceSchema = Field(
        default_factory=dict,
        title="Resource",
        description="Resource that was affected by the event",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        title="Metadata",
        description="Metadata of the event that was performed",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        title="Timestamp",
        description="Timestamp of the event that was performed",
    )

    class Config:
        schema_extra = {
            "example": {
                "category": "audit",
                "tags": {
                    "application": "spectratrace_api",
                    "environment": "staging",
                },
                "method": "POST",
                "status": "success",
                "level": "info",
                "event": {
                    "id": "1",
                    "name": "Login",
                    "type": "Authentication",
                    "stage": 1,
                    "totalDuration": 0.1,
                    "affectedResources": 1,
                    "latency": 0.05,
                    "cpuUsage": 0.5,
                    "memoryUsage": 0.2,
                    "detail": {
                        "username": "johndoe",
                    },
                    "description": "User logged in successfully",
                },
                "actor": {
                    "origin": "127.0.0.1",
                    "detail": {
                        "username": "johndoe",
                    },
                },
                "resource": {
                    "id": "1",
                    "name": "User",
                    "type": "User",
                    "detail": {
                        "username": "johndoe",
                    },
                },
                "metadata": {
                    "key": "value",
                },
                "timestamp": "2021-01-01T00:00:00.000Z",
            },
        }

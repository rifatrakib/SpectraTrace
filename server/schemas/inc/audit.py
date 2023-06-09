from datetime import datetime
from typing import List, Union

from pydantic import Field, validator

from server.schemas.base import BaseRequestSchema
from server.schemas.common.audit import ActorSchema, EventSchema, MetadataSchema, ResourceSchema, TagSchema


class AuditRequestSchema(BaseRequestSchema):
    category: str = Field(title="Category", description="Category of the event, to be used as measurement in InfluxDB")
    source_information: TagSchema = Field(title="Source Information", description="Tags of InfluxDB measurement")
    method: str = Field(title="Method", description="Method that was used to perform the action")
    status: str = Field(title="Status", description="Status of the event that was performed")
    level: str = Field(title="Level", description="Level of the event that was performed")
    event: EventSchema = Field(title="Event", description="Event that was performed")
    actor: ActorSchema = Field(title="Actor", description="Actor that performed the event")
    resource: ResourceSchema = Field(
        default_factory=dict,
        title="Resource",
        description="Resource that was affected by the event",
    )
    metadata: List[MetadataSchema] = Field(
        default_factory=list,
        title="Metadata",
        description="Metadata of the event that was performed",
    )

    class Config:
        schema_extra = {
            "example": {
                "category": "audit",
                "source_information": {
                    "application": "spectratrace_api",
                    "environment": "staging",
                },
                "method": "POST",
                "status": "success",
                "level": "info",
                "event": {
                    "name": "Login",
                    "type": "Authentication",
                    "stage": 1,
                    "total_duration": 0.1,
                    "affected_resources": 1,
                    "latency": 0.05,
                    "cpu_usage": 0.5,
                    "memory_usage": 0.2,
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
                "metadata": [
                    {
                        "is_metric": True,
                        "name": "login_time",
                        "value": 0.1,
                    },
                ],
            },
        }


class AuditSchema(AuditRequestSchema):
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        title="Timestamp",
        description="Timestamp of the event that was performed",
    )

    class Config:
        schema_extra = {
            "example": {
                "category": "audit",
                "source_information": {
                    "application": "spectratrace_api",
                    "environment": "staging",
                },
                "method": "POST",
                "status": "success",
                "level": "info",
                "event": {
                    "name": "Login",
                    "type": "Authentication",
                    "stage": 1,
                    "total_duration": 0.1,
                    "affected_resources": 1,
                    "latency": 0.05,
                    "cpu_usage": 0.5,
                    "memory_usage": 0.2,
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
                "metadata": [
                    {
                        "is_metric": True,
                        "name": "login_time",
                        "value": 0.1,
                    },
                ],
            },
            "timestamp": "2021-01-01T00:00:00.000000+00:00",
        }


class AuditRetrievalRequestSchema(BaseRequestSchema):
    app: str = Field()
    env: str = Field()
    category: Union[str, None] = Field(default=None)
    method: Union[str, None] = Field(default=None)
    status: Union[str, None] = Field(default=None)
    origin: Union[str, None] = Field(default=None)
    start: Union[datetime, str] = Field(default="1d")
    stop: Union[datetime, str] = Field(default="now()")

    @validator("start")
    def convert_start(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"-{v}"

    @validator("stop")
    def convert_stop(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%dT%H:%M:%SZ")
        return v if v == "now()" else f"-{v}"

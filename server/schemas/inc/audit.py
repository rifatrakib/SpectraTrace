from datetime import datetime
from typing import Any, Dict, List, Union

from pydantic import Field

from server.schemas.base import BaseRequestSchema


class MetadataSchema(BaseRequestSchema):
    is_metric: bool = Field(default=False, title="Is Metric", description="Whether the event is a metric or not")
    name: str = Field(title="Name", description="Name of the metric")
    value: Union[int, float, str, bool] = Field(title="Value", description="Value of the metric")

    class Config:
        schema_extra = {
            "example": {
                "is_metric": True,
                "name": "login_time",
                "value": 0.1,
            },
        }


class TagSchema(BaseRequestSchema):
    application: str = Field(title="Application Name", description="Name of the application that generated the event")
    environment: str = Field(
        title="Environment",
        description="Environment of the application the event was generated in",
    )

    class Config:
        schema_extra = {
            "example": {
                "application": "spectratrace-api",
                "environment": "staging",
            },
        }


class EventSchema(BaseRequestSchema):
    id: str = Field(title="Event ID", description="Unique ID of the event")
    name: str = Field(title="Event Name", description="Name of the event that was performed")
    type: str = Field(title="Event Type", description="Type of the event that was performed")
    stage: int = Field(title="Stage", description="Stage of the event in a sequence of events")
    total_duration: Union[float, None] = Field(
        default=None, title="Total Duration", description="Duration of the event in milliseconds", gt=0
    )
    affected_resources: int = Field(
        default=0, title="Affected Resources", description="Number of resources affected by the event", ge=0
    )
    latency: Union[float, None] = Field(
        default=None, title="Latency", description="Latency of the event in milliseconds", gt=0
    )
    cpu_usage: Union[float, None] = Field(
        default=None, title="CPU Usage", description="CPU usage (%) of the event", ge=0, le=100
    )
    memory_usage: Union[float, None] = Field(
        default=None, title="Memory Usage", description="Memory usage (%) of the event", ge=0, le=100
    )
    detail: Dict[str, Any] = Field(
        default_factory=dict,
        title="Event Data",
        description="Arbitrary data of the event that was performed",
    )
    description: Union[str, None] = Field(
        default=None,
        title="Description of the event",
        description="Descriptive details of the event that was performed",
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "1",
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
        }


class ActorSchema(BaseRequestSchema):
    origin: str = Field(title="Origin", description="IP address of the origin of the event")
    detail: Dict[str, Any] = Field(
        default_factory=dict,
        title="User Data",
        description="Information of actor performing the event",
    )

    class Config:
        schema_extra = {
            "example": {
                "origin": "127.0.0.1",
                "detail": {
                    "username": "johndoe",
                },
            },
        }


class ResourceSchema(BaseRequestSchema):
    id: str = Field(title="Resource ID", description="Unique ID of the resource")
    name: str = Field(title="Resource Name", description="Name of the resource")
    type: str = Field(title="Resource Type", description="Type of the resource")
    detail: Dict[str, Any] = Field(
        default_factory=dict,
        title="Resource Data",
        description="Arbitrary data of the resource that was affected",
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "1",
                "name": "User",
                "type": "User",
                "detail": {
                    "username": "johndoe",
                },
            },
        }


class AuditRequestSchema(BaseRequestSchema):
    category: str = Field(title="Category", description="Category of the event, to be used as measurement in InfluxDB")
    source_information: TagSchema = Field(title="Source Information", description="Tags of InfluxDB measurement")
    method: str = Field(title="Method", description="Method that was used to perform the action")
    status: str = Field(title="Status", description="Status of the event that was performed")
    level: str = Field(title="Level", description="Level of the event that was performed")
    event: EventSchema = Field(title="Event", description="Event that was performed")
    actor: ActorSchema = Field(title="Actor", description="Actor that performed the event")
    resources: List[ResourceSchema] = Field(
        default_factory=list,
        title="Resources",
        description="Resource that was affected by the event",
    )
    metadata: List[MetadataSchema] = Field(
        default_factory=list,
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
                "source_information": {
                    "application": "spectratrace-api",
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
                "resources": [
                    {
                        "id": "1",
                        "name": "User",
                        "type": "User",
                        "detail": {
                            "username": "johndoe",
                        },
                    },
                ],
                "metadata": [
                    {
                        "is_metric": True,
                        "name": "login_time",
                        "value": 0.1,
                    },
                ],
            },
        }

from datetime import datetime
from typing import Any, Dict, Union

from pydantic import Field, IPvAnyAddress

from server.schemas.base import BaseRequestSchema


class TagSchema(BaseRequestSchema):
    application: str = Field(title="Application Name", description="Name of the application that generated the event")
    environment: str = Field(
        title="Environment",
        description="Environment of the application the event was generated in",
    )


class EventSchema(BaseRequestSchema):
    id: str = Field(title="Event ID", description="Unique ID of the event")
    name: str = Field(title="Event Name", description="Name of the event that was performed")
    type: str = Field(title="Event Type", description="Type of the event that was performed")
    stage: int = Field(title="Stage", description="Stage of the event in a sequence of events")
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


class ActorSchema(BaseRequestSchema):
    origin: IPvAnyAddress = Field(title="Origin", description="IP address of the origin of the event")
    detail: Dict[str, Any] = Field(
        default_factory=dict,
        title="User Data",
        description="Information of actor performing the event",
    )


class ResourceSchema(BaseRequestSchema):
    id: str = Field(title="Resource ID", description="Unique ID of the resource")
    name: str = Field(title="Resource Name", description="Name of the resource")
    type: str = Field(title="Resource Type", description="Type of the resource")
    detail: Dict[str, Any] = Field(
        default_factory=dict,
        title="Resource Data",
        description="Arbitrary data of the resource that was affected",
    )


class AuditRequestSchema(BaseRequestSchema):
    category: str = Field(title="Category", description="Category of the event, to be used as measurement in InfluxDB")
    source_information: TagSchema = Field(title="Source Information", description="Tags of InfluxDB measurement")
    method: str = Field(title="Method", description="Method that was used to perform the action")
    status: str = Field(title="Status", description="Status of the event that was performed")
    level: str = Field(title="Level", description="Level of the event that was performed")
    event: EventSchema = Field(title="Event", description="Event that was performed")
    actor: ActorSchema = Field(title="Actor", description="Actor that performed the event")
    resource: ResourceSchema = Field(
        default=None,
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

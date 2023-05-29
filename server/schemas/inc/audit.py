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


class AuditRequestSchema(BaseRequestSchema):
    category: str = Field(title="Category", description="Category of the event, to be used as measurement in InfluxDB")
    source_information: TagSchema = Field(title="Source Information", description="Tags of InfluxDB measurement")
    method: str = Field(title="Method", description="Method that was used to perform the action")
    event_id: str = Field(title="Event ID", description="Unique ID of the event")
    event_name: str = Field(title="Event Name", description="Name of the event that was performed")
    event_type: str = Field(title="Event Type", description="Type of the event that was performed")
    correlation_id: Union[str, None] = Field(
        default=None,
        title="Correlation ID",
        description="Unique ID of a related event",
    )
    origin: IPvAnyAddress = Field(title="Origin", description="IP address of the origin of the event")
    user_agent: str = Field(title="User Agent", description="User agent of the origin of the event")
    event_data: Dict[str, Any] = Field(
        default_factory=dict,
        title="Event Data",
        description="Arbitrary data of the event that was performed",
    )
    event_details: Union[str, None] = Field(
        default=None,
        title="Event Details",
        description="Descriptive details of the event that was performed",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        title="Timestamp",
        description="Timestamp of the event that was performed",
    )

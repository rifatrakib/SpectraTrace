import json
from typing import List, Union

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from server.schemas.inc.audit import AuditRequestSchema


def create_influxdb_point(
    data: Union[AuditRequestSchema, List[AuditRequestSchema]],
) -> Union[Point, List[Point]]:
    if isinstance(data, list):
        return [create_influxdb_point(item) for item in data]

    return (
        Point(data.category)
        .tag("application", data.source_information.application)
        .tag("environment", data.source_information.environment)
        .field("method", data.method)
        .field("status", data.status)
        .field("level", data.level)
        .field("event_id", data.event.id)
        .field("event_name", data.event.name)
        .field("event_type", data.event.type)
        .field("event_stage", data.event.stage)
        .field("event_description", data.event.description)
        .field("event_detail", json.dumps(data.event.detail))
        .field("actor_origin", str(data.actor.origin))
        .field("actor_detail", json.dumps(data.actor.detail))
        .field("resource_id", data.resource.id)
        .field("resource_name", data.resource.name)
        .field("resource_type", data.resource.type)
        .field("resource_detail", json.dumps(data.resource.detail))
        .field("metadata", json.dumps(data.metadata))
        .time(data.timestamp)
    )


def add_new_point_to_bucket(
    client: InfluxDBClient,
    bucket: str,
    data: Union[AuditRequestSchema, List[AuditRequestSchema]],
) -> None:
    point: Point = create_influxdb_point(data)
    with client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, record=point)

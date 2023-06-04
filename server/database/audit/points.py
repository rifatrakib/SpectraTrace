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

    point = (
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
        .field("event_duration", data.event.total_duration)
        .field("affected_resources", data.event.affected_resources)
        .field("latency", data.event.latency)
        .field("cpu_usage", data.event.cpu_usage)
        .field("memory_usage", data.event.memory_usage)
        .field("event_description", data.event.description)
        .field("event_detail", json.dumps(data.event.detail))
        .field("actor_origin", str(data.actor.origin))
        .field("actor_detail", json.dumps(data.actor.detail))
    )

    resources = [resource.dict() for resource in data.resources]
    point.field("resources", json.dumps(resources))

    metadata = {}
    for item in data.metadata:
        if item.is_metric:
            point.field(item.name, item.value)
        else:
            metadata[item.name] = item.value

    point.field("metadata", json.dumps(metadata))
    return point.time(data.timestamp)


def add_new_point_to_bucket(
    client: InfluxDBClient,
    bucket: str,
    data: Union[AuditRequestSchema, List[AuditRequestSchema]],
) -> None:
    point: Point = create_influxdb_point(data)
    with client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, record=point)


def read_points_from_bucket(
    client: InfluxDBClient,
    organization: str,
    bucket: str,
    measurement: str,
) -> List[Point]:
    query = f'from(bucket: "{bucket}") |> range(start: -1d) |> filter(fn: (r) => r._measurement == "{measurement}")'
    with client:
        query_api = client.query_api()
        result = query_api.query(query=query, org=organization)
        return list(result)

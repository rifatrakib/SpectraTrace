import json
from typing import List

from helpers.models import AuditRequestSchema
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


def create_influxdb_point(data: List[AuditRequestSchema]) -> List[Point]:
    points = []

    for index, event_data in enumerate(data):
        point = (
            Point(event_data.category)
            .tag("application", event_data.source_information.application)
            .tag("environment", event_data.source_information.environment)
            .field("method", event_data.method)
            .field("status", event_data.status)
            .field("level", event_data.level)
            .field("event_id", event_data.event.id)
            .field("event_name", event_data.event.name)
            .field("event_type", event_data.event.type)
            .field("event_stage", index + 1)
            .field("event_duration", event_data.event.total_duration)
            .field("affected_resources", event_data.event.affected_resources)
            .field("latency", event_data.event.latency)
            .field("cpu_usage", event_data.event.cpu_usage)
            .field("memory_usage", event_data.event.memory_usage)
            .field("event_description", event_data.event.description)
            .field("actor_origin", event_data.actor.origin)
        )

        if event_data.event.detail:
            point.field("event_detail", json.dumps(event_data.event.detail))

        if event_data.actor.detail:
            point.field("actor_detail", json.dumps(event_data.actor.detail))

        resources = [resource.dict() for resource in event_data.resources]
        point.field("resources", json.dumps(resources))

        metadata = {}
        for item in event_data.metadata:
            if item.is_metric:
                point.field(item.name, item.value)
            else:
                metadata[item.name] = item.value

        if metadata:
            point.field("metadata", json.dumps(metadata))

        point.time(event_data.timestamp)
        points.append(point)

    return points


def add_new_point_to_bucket(
    client: InfluxDBClient,
    bucket: str,
    data: List[AuditRequestSchema],
) -> None:
    point: Point = create_influxdb_point(data)
    with client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, record=point)

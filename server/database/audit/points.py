import json
from functools import lru_cache
from typing import List

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.flux_table import FluxTable

from server.schemas.inc.audit import AuditRetrievalRequestSchema


@lru_cache()
def get_invariant_fields() -> List[str]:
    with open("server/templates/static/invariant-fields.json", "r") as reader:
        data = json.loads(reader.read())
    return data["invariant_fields"]


def proccess_points(tables: List[FluxTable]):
    result = []
    invariant_fields = get_invariant_fields()

    for table in tables:
        for record in table.records:
            values = record.values
            variant_fields = list(filter(lambda x: x not in invariant_fields, values.keys()))
            item = {
                "category": values["_measurement"],
                "tags": {
                    "application": values["application"],
                    "environment": values["environment"],
                },
                "method": values["method"],
                "status": values["status"],
                "level": values["level"],
                "event": {
                    "id": values["event_id"],
                    "name": values["event_name"],
                    "type": values["event_type"],
                    "stage": values["event_stage"],
                    "total_duration": values["event_duration"],
                    "affected_resources": values["affected_resources"],
                    "latency": values["latency"],
                    "cpu_usage": values["cpu_usage"],
                    "memory_usage": values["memory_usage"],
                    "description": values["event_description"],
                },
                "actor": {
                    "origin": values["actor_origin"],
                },
                "resource": {
                    "id": values["resource_id"],
                    "name": values["resource_name"],
                    "type": values["resource_type"],
                },
                "timestamp": values["_time"],
            }

            if values.get("event_detail", None):
                item["event"]["detail"] = json.loads(values["event_detail"])
            if values.get("actor_detail", None):
                item["actor"]["detail"] = json.loads(values["actor_detail"])
            if values.get("resource_detail", None):
                item["resource"]["detail"] = json.loads(values["resource_detail"])

            metadata = {}
            if values.get("metadata", None):
                for key, value in json.loads(values["metadata"]).items():
                    try:
                        metadata[key] = json.loads(value)
                    except ValueError:
                        metadata[key] = value

            for key in variant_fields:
                metadata[key] = values[key]

            item["metadata"] = metadata
            result.append(item)

    return result


def build_influxdb_query(
    bucket: str,
    parameters: AuditRetrievalRequestSchema,
):
    query = f'from(bucket: "{bucket}") |> range(start: {parameters.start}, stop: {parameters.stop})'

    if parameters.category:
        query += f'|> filter(fn: (r) => r["_measurement"] == "{parameters.category}")'

    query += f' |> filter(fn: (r) => r["application"] == "{parameters.app}")'
    if parameters.env:
        query += f' |> filter(fn: (r) => r["environment"] == "{parameters.env}")'

    query += ' |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")'

    if parameters.method:
        query += f' |> filter(fn: (r) => r["method"] == "{parameters.method}")'
    if parameters.status:
        query += f' |> filter(fn: (r) => r["status"] == "{parameters.status}")'
    if parameters.origin:
        query += f' |> filter(fn: (r) => r["actor_origin"] == "{parameters.origin}")'

    return query


def read_points_from_bucket(
    client: InfluxDBClient,
    organization: str,
    bucket: str,
    parameters: AuditRetrievalRequestSchema,
) -> List[Point]:
    query = build_influxdb_query(bucket=bucket, parameters=parameters)

    with client:
        query_api = client.query_api()
        result = query_api.query(query=query, org=organization)

    result = proccess_points(result)
    return result


def read_list_of_available_metrics(
    client: InfluxDBClient,
    organization: str,
    bucket: str,
):
    query = (
        f'from(bucket: "{bucket}")'
        " |> range(start: 0)"
        ' |> keep(columns: ["_field"])'
        " |> group()"
        ' |> distinct(column: "_field")'
        ' |> yield(name: "fieldKeys")'
    )

    with client:
        query_api = client.query_api()
        result = query_api.query(query=query, org=organization)

    metrics = [record.values["_value"] for table in result for record in table.records]
    invariant_fields = get_invariant_fields()
    metrics = list(filter(lambda x: x not in invariant_fields, metrics))

    return metrics + ["affected_resources", "event_duration", "latency", "cpu_usage", "memory_usage"]


def process_metric_result(tables: List[FluxTable], metric_name: str):
    result = []
    for table in tables:
        for record in table.records:
            values = record.values
            result.append(
                {
                    "range": f'{values["_start"]} - {values["_stop"]}',
                    "value": values[metric_name],
                },
            )

    return result


def calculate_metrics_from_bucket(
    client: InfluxDBClient,
    organization: str,
    bucket: str,
    parameters: AuditRetrievalRequestSchema,
    interval: str,
    metric_name: str,
    agg: str,
) -> List[Point]:
    query = build_influxdb_query(bucket=bucket, parameters=parameters)
    query += f' |> window(every: {interval}) |> {agg}(column: "{metric_name}")'

    with client:
        query_api = client.query_api()
        result = query_api.query(query=query, org=organization)

    result = process_metric_result(result, metric_name)
    return result

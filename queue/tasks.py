import json
from typing import List

from celery import Celery
from helpers.config import settings
from helpers.models import AuditRequestSchema
from helpers.push import add_new_point_to_bucket
from influxdb_client import InfluxDBClient
from pydantic import parse_obj_as

app = Celery("tasks", broker=settings.RABBITMQ_URI, backend="rpc://")


@app.task()
def log_event(url, token, org, bucket, data):
    client: InfluxDBClient = InfluxDBClient(url=url, token=token, org=org)
    data = parse_obj_as(List[AuditRequestSchema], json.loads(data))
    add_new_point_to_bucket(client=client, bucket=bucket, data=data)

from typing import Any, Dict, List

from celery import Celery
from helpers.config import settings
from helpers.models import AuditRequestSchema
from helpers.push import add_new_point_to_bucket
from influxdb_client import InfluxDBClient
from pydantic import parse_obj_as

app = Celery("tasks", broker=settings.BROKER_URI, backend=settings.BROKER_URI)
app.conf.acks_on_failure_or_timeout = True
app.conf.reject_on_worker_lost = True
app.conf.task_acks_late = True


@app.task()
def log_event(
    url: str,
    token: str,
    org: str,
    bucket: str,
    data: List[Dict[str, Any]],
):
    client: InfluxDBClient = InfluxDBClient(url=url, token=token, org=org)
    data = parse_obj_as(List[AuditRequestSchema], data)
    add_new_point_to_bucket(client=client, bucket=bucket, data=data)

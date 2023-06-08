from typing import List

from celery import Celery

from server.config.factory import settings
from server.models.users import UserAccount
from server.schemas.inc.audit import AuditRequestSchema, AuditSchema

celery_app = Celery("worker", broker=settings.BROKER_URI, backend=settings.BROKER_URI)


def publish_task(admin: UserAccount, bucket: str, event_data: List[AuditRequestSchema]):
    data = []
    if isinstance(event_data, list):
        data = [AuditSchema(**event.dict()).dict() for event in event_data]
    else:
        data.append(AuditSchema(**event_data.dict()).dict())

    params = {
        "url": f"http://{settings.INFLUXDB_HOST}:{settings.INFLUXDB_PORT}",
        "token": admin.api_token,
        "org": settings.INFLUXDB_ORG,
        "bucket": bucket,
        "data": data,
    }
    celery_app.send_task("tasks.log_event", kwargs=params)

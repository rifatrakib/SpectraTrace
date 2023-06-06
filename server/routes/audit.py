import json
from typing import Any, Dict, List, Union

from celery import Celery
from fastapi import APIRouter, Body, Depends, HTTPException, status
from influxdb_client import InfluxDBClient

from server.config.factory import settings
from server.database.audit.points import read_points_from_bucket
from server.models.users import UserAccount
from server.schemas.inc.audit import AuditRequestSchema
from server.security.dependencies.audit import verify_user_access
from server.security.dependencies.sessions import get_influxdb_admin, get_influxdb_client
from server.utils.enums import Tags

router = APIRouter(
    prefix="/audit",
    tags=[Tags.audit],
)

celery_app = Celery("worker", broker=settings.BROKER_URI, backend=settings.BROKER_URI)


@router.post(
    "/log",
    summary="Log audit event",
    description="Log one or more audit event(s)",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def log_audit_event(
    admin: UserAccount = Depends(get_influxdb_admin),
    current_user: Dict[str, Any] = Depends(verify_user_access),
    event_data: Union[AuditRequestSchema, List[AuditRequestSchema]] = Body(
        title="Audit Event",
        description="Audit event to be logged",
    ),
):
    try:
        data = []
        if isinstance(event_data, list):
            data = [json.loads(event.json()) for event in event_data]
        else:
            data.append(json.loads(event_data.json()))

        params = {
            "url": f"http://{settings.INFLUXDB_HOST}:{settings.INFLUXDB_PORT}",
            "token": admin.api_token,
            "org": settings.INFLUXDB_ORG,
            "bucket": current_user["username"],
            "data": json.dumps(data),
        }
        celery_app.send_task("tasks.log_event", kwargs=params)
    except HTTPException as e:
        raise e


@router.get(
    "/log",
    summary="Read log audit events",
    description="Read audit events from the audit log",
)
async def read_logs(
    current_user: Dict[str, Any] = Depends(verify_user_access),
    influx_client: InfluxDBClient = Depends(get_influxdb_client),
):
    try:
        data = read_points_from_bucket(
            client=influx_client,
            organization=settings.INFLUXDB_ORG,
            bucket=current_user["username"],
            measurement="audit",
        )
        return data
    except HTTPException as e:
        raise e

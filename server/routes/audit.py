from typing import Any, Dict, List, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from influxdb_client import InfluxDBClient

from server.config.factory import settings
from server.database.audit.points import read_points_from_bucket
from server.models.users import UserAccount
from server.schemas.inc.audit import AuditRequestSchema
from server.security.dependencies.audit import verify_user_access
from server.security.dependencies.auth import is_user_active
from server.security.dependencies.sessions import get_influxdb_admin, get_influxdb_client
from server.utils.enums import Tags
from server.utils.tasks import publish_task

router = APIRouter(
    prefix="/audit",
    tags=[Tags.audit],
)


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
        publish_task(admin=admin, bucket=current_user["username"], event_data=event_data)
    except HTTPException as e:
        raise e


@router.get(
    "/log",
    summary="Read log audit events",
    description="Read audit events from the audit log",
)
async def read_logs(
    q: str = Query(),
    current_user: Dict[str, Any] = Depends(is_user_active),
    influx_client: InfluxDBClient = Depends(get_influxdb_client),
):
    try:
        data = read_points_from_bucket(
            client=influx_client,
            organization=settings.INFLUXDB_ORG,
            bucket=current_user.username,
            measurement=q,
        )
        return data
    except HTTPException as e:
        raise e

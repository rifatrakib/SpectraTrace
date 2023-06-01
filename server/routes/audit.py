from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, status
from influxdb_client import InfluxDBClient

from server.database.audit.points import add_new_point_to_bucket
from server.schemas.base import MessageResponseSchema
from server.schemas.inc.audit import AuditRequestSchema
from server.security.dependencies.audit import verify_user_access
from server.security.dependencies.sessions import get_influxdb_client
from server.utils.enums import Tags

router = APIRouter(
    prefix="/audit",
    tags=[Tags.audit],
)


@router.post(
    "/log",
    summary="Log an audit event",
    description="Log an audit event",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def log_audit_event(
    current_user: Dict[str, Any] = Depends(verify_user_access),
    influx_client: InfluxDBClient = Depends(get_influxdb_client),
    event_data: AuditRequestSchema = Body(title="Audit Event", description="Audit event to be logged"),
):
    try:
        add_new_point_to_bucket(
            client=influx_client,
            bucket=current_user["username"],
            data=event_data,
        )
        return {"msg": "Audit event logged."}
    except HTTPException as e:
        raise e

from fastapi import APIRouter, Body, Depends, HTTPException, status

from server.schemas.base import MessageResponseSchema
from server.schemas.inc.audit import AuditRequestSchema
from server.security.dependencies.audit import verify_user_access
from server.utils.enums import Tags

router = APIRouter(
    prefix="/audit",
    tags=[Tags.audit],
    dependencies=[Depends(verify_user_access)],
)


@router.post(
    "/log",
    summary="Log an audit event",
    description="Log an audit event",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def log_audit_event(
    event_data: AuditRequestSchema = Body(title="Audit Event", description="Audit event to be logged")
):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)

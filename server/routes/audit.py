from typing import Any, Dict, List, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from influxdb_client import InfluxDBClient

from server.config.factory import settings
from server.database.audit.points import (
    calculate_metrics_count_from_bucket,
    calculate_metrics_from_bucket,
    read_event_trail,
    read_list_of_available_metrics,
    read_points_from_bucket,
)
from server.models.users import UserAccount
from server.schemas.inc.audit import AuditRequestSchema, AuditRetrievalRequestSchema
from server.schemas.out.audit import AuditResponseSchema, MetricCountResponseSchema, MetricResponseSchema
from server.schemas.out.auth import TokenUser
from server.security.dependencies.audit import log_retrieval_query_parameters, verify_user_access
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
    response_model=List[AuditResponseSchema],
)
async def read_logs(
    current_user: TokenUser = Depends(is_user_active),
    influx_client: InfluxDBClient = Depends(get_influxdb_client),
    parameters: AuditRetrievalRequestSchema = Depends(log_retrieval_query_parameters),
    page: int = Query(default=1, description="Page number", example=1),
):
    try:
        data = read_points_from_bucket(
            client=influx_client,
            organization=settings.INFLUXDB_ORG,
            bucket=current_user.username,
            parameters=parameters,
            offset=(page - 1) * 50,
        )
        return data
    except HTTPException as e:
        raise e


@router.get(
    "/log/{event_id}",
    summary="Read log audit events",
    description="Read audit events from the audit log",
    response_model=List[AuditResponseSchema],
)
async def read_single_event(
    current_user: TokenUser = Depends(is_user_active),
    influx_client: InfluxDBClient = Depends(get_influxdb_client),
    event_id: str = Path(..., description="Event ID", example="1234567890"),
):
    try:
        data = read_event_trail(
            client=influx_client,
            organization=settings.INFLUXDB_ORG,
            bucket=current_user.username,
            event_id=event_id,
        )
        return data
    except HTTPException as e:
        raise e


@router.get(
    "/metrics",
    summary="Read a list of audit metrics",
    description="Read a list of audit metrics from the audit log",
    response_model=List[str],
)
async def read_metrics_list(
    current_user: TokenUser = Depends(is_user_active),
    influx_client: InfluxDBClient = Depends(get_influxdb_client),
):
    try:
        metrics = read_list_of_available_metrics(
            client=influx_client,
            organization=settings.INFLUXDB_ORG,
            bucket=current_user.username,
        )
        return metrics
    except HTTPException as e:
        raise e


@router.get(
    "/metrics/{metric_name}",
    summary="Calculate a metric",
    description="Calculate a metric from the audit log",
    response_model=List[MetricResponseSchema],
)
async def calculate_metric(
    current_user: TokenUser = Depends(is_user_active),
    influx_client: InfluxDBClient = Depends(get_influxdb_client),
    parameters: AuditRetrievalRequestSchema = Depends(log_retrieval_query_parameters),
    interval: str = Query(default="1m", description="Interval to calculate the metric"),
    metric_name: str = Path(..., description="Name of the metric to be calculated", example="cpu_usage"),
    agg: str = Query(default="mean", description="Aggregation function to be used", example="sum"),
    group_by: Union[str, None] = Query(default=None, description="Field to group by", example="status"),
):
    try:
        data = calculate_metrics_from_bucket(
            client=influx_client,
            organization=settings.INFLUXDB_ORG,
            bucket=current_user.username,
            parameters=parameters,
            interval=interval,
            metric_name=metric_name,
            agg=agg,
            group_by=group_by,
        )
        return data
    except HTTPException as e:
        raise e


@router.get(
    "/metrics/{metric_name}/count",
    summary="Calculate a metric",
    description="Calculate a metric from the audit log",
    response_model=List[MetricCountResponseSchema],
)
async def calculate_metric_count(
    current_user: TokenUser = Depends(is_user_active),
    influx_client: InfluxDBClient = Depends(get_influxdb_client),
    parameters: AuditRetrievalRequestSchema = Depends(log_retrieval_query_parameters),
    interval: str = Query(default="1m", description="Interval to calculate the metric"),
    metric_name: str = Path(..., description="Name of the metric to be calculated", example="status"),
):
    try:
        data = calculate_metrics_count_from_bucket(
            client=influx_client,
            organization=settings.INFLUXDB_ORG,
            bucket=current_user.username,
            parameters=parameters,
            interval=interval,
            metric_name=metric_name,
        )
        return data
    except HTTPException as e:
        raise e

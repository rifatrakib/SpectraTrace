from typing import Any, Dict

from server.config.factory import settings
from server.models.users import UserAccount
from server.schemas.inc.audit import AuditRequestSchema, MetadataSchema
from server.utils.utilities import get_event_template


def db_initialization_event(execution_time: float, sql: str) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("rdbms-events")

    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "initial configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.3  # sample value
    event_data.event.memory_usage = 0.1  # sample value
    event_data.event.detail["sql"] = sql
    event_data.event.description = "Create necessary tables in PostgreSQL database"
    event_data.actor.detail["location"] = "server/main.py - line 146"
    event_data.resource.detail["database"] = settings.POSTGRES_DB
    event_data.resource.detail["tables"] = ["accounts"]

    return event_data


def influxdb_onboarding_event(
    execution_time: float,
    url: str,
    payload: Dict[str, str],
    headers: Dict[str, str],
    response: Dict[str, Any],
) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("influx-events")

    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "initial configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.05  # sample value
    event_data.event.memory_usage = 0.15  # sample value
    event_data.event.detail["url"] = url
    event_data.event.detail["method"] = "POST"
    event_data.event.detail["payload"] = payload
    event_data.event.detail["headers"] = headers
    event_data.event.description = "Create admin account in InfluxDB database via HTTP endpoint"
    event_data.actor.detail["location"] = "server/main.py::on_startup - line 46"
    event_data.resource.detail["bucket"] = settings.INFLUXDB_USER
    event_data.resource.detail["organization"] = settings.INFLUXDB_ORG
    event_data.resource.detail["api_token"] = response["auth"]["token"]
    event_data.resource.detail["permissions"] = response["auth"]["permissions"]

    return event_data


def admin_account_create_event(
    execution_time: float,
    sql: str,
    user: UserAccount,
) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("rdbms-events")

    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "initial configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.25  # sample value
    event_data.event.memory_usage = 0.2  # sample value
    event_data.event.detail["sql"] = sql
    event_data.event.description = "Create admin account in PostgreSQL database"
    event_data.actor.detail["location"] = "server/main.py::on_startup - line 80"
    event_data.resource.detail["database"] = settings.POSTGRES_DB
    event_data.resource.detail["tables"] = ["accounts"]
    event_data.metadata = [
        MetadataSchema(
            is_metric=False,
            name="admin_account",
            value=user.json(),
        ),
    ]

    return event_data


def check_admin_account_event(
    execution_time: float,
    sql: str,
    user: UserAccount,
) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("rdbms-events")

    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "initial configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.1  # sample value
    event_data.event.memory_usage = 0.1  # sample value
    event_data.event.detail["sql"] = sql
    event_data.event.description = "Check if admin account exists in PostgreSQL database"
    event_data.actor.detail["location"] = "server/main.py::on_startup - line 101"
    event_data.resource.detail["database"] = settings.POSTGRES_DB
    event_data.resource.detail["tables"] = ["accounts"]

    if user:
        event_data.metadata = [
            MetadataSchema(
                is_metric=False,
                name="admin_account",
                value=user.json(),
            ),
        ]

    return event_data

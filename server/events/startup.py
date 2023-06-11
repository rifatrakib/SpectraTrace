import json
from typing import Any, Dict

from server.config.factory import settings
from server.events.templates import get_event_template
from server.models.users import UserAccount
from server.schemas.inc.audit import AuditRequestSchema


def db_initialization_event(execution_time: float) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("rdbms-events")

    event_data.method = "write"
    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.3  # sample value
    event_data.event.memory_usage = 0.1  # sample value
    event_data.event.description = "Create necessary tables in PostgreSQL database"
    event_data.actor.detail = {"agent": "SQLAlchemy"}
    event_data.resource.detail = {"database_instance": settings.RDS_URI}

    return event_data


def influxdb_onboarding_event(
    execution_time: float,
    url: str,
    payload: Dict[str, str],
    headers: Dict[str, str],
    response: Dict[str, Any],
) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("influx-events")

    event_data.method = "POST"
    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.05  # sample value
    event_data.event.memory_usage = 0.15  # sample value
    event_data.event.detail["url"] = url
    event_data.event.detail["payload"] = payload
    event_data.event.detail["headers"] = headers
    event_data.event.description = "Create admin account in InfluxDB database via HTTP endpoint"
    event_data.actor.detail = {"agent": "requests"}
    event_data.resource.detail = {
        "bucket": settings.INFLUXDB_USER,
        "organization": settings.INFLUXDB_ORG,
        "api_token": response["auth"]["token"],
        "permissions": response["auth"]["permissions"],
    }

    return event_data


def admin_account_create_event(
    execution_time: float,
    user: UserAccount,
) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("rdbms-events")

    event_data.method = "write"
    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.25  # sample value
    event_data.event.memory_usage = 0.2  # sample value
    event_data.event.description = "Create admin account in PostgreSQL database"
    event_data.actor.detail = {
        "agent": "SQLAlchemy",
        "model": "UserAccount",
        "parameters": json.loads(user.json()),
    }
    event_data.resource.detail = {"database": settings.POSTGRES_DB, "table": "accounts"}

    return event_data


def check_admin_account_event(execution_time: float) -> AuditRequestSchema:
    event_data: AuditRequestSchema = get_event_template("rdbms-events")

    event_data.method = "read"
    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time / 3 * 2
    event_data.event.cpu_usage = 0.1  # sample value
    event_data.event.memory_usage = 0.1  # sample value
    event_data.event.description = "Check if admin account exists in PostgreSQL database"
    event_data.actor.detail = {"agent": "SQLAlchemy", "model": "UserAccount"}
    event_data.resource.detail = {"database": settings.POSTGRES_DB, "table": "accounts"}

    return event_data

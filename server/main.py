import io
import logging
from time import time

import requests
from fastapi import FastAPI
from pydantic import parse_file_as
from sqlmodel import Session, create_engine, select

from server.config.factory import settings
from server.database.managers import create_db_and_tables, ping_redis_server
from server.docs.manager import read_api_metadata, read_tags_metadata
from server.models.users import UserAccount
from server.routes.audit import router as audit_router
from server.routes.auth import router as auth_router
from server.routes.user import router as user_router
from server.schemas.base import HealthResponseSchema
from server.schemas.inc.audit import AuditRequestSchema, MetadataSchema
from server.security.auth.authentication import pwd_context
from server.utils.enums import Tags
from server.utils.generators import generate_random_key
from server.utils.tasks import publish_task

app = FastAPI(
    **read_api_metadata(),
    openapi_tags=read_tags_metadata(),
)


def influxdb_onboarding(base_url, user, password, organization):
    event_data: AuditRequestSchema = parse_file_as(
        type_=AuditRequestSchema,
        path="server/templates/events/influx-events.json",
    )

    payload = {"username": user, "password": password, "org": organization, "bucket": user}
    headers = {
        "sec-ch-ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        "sec-ch-ua-platform": '"Windows"',
        "Referer": f"{base_url}/onboarding/1",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0"
            " Safari/537.36"
        ),
        "content-type": "application/json",
    }

    start_time = time()
    r = requests.post(f"{base_url}/api/v2/setup", headers=headers, json=payload)
    execution_time = (time() - start_time) * 1000
    response = r.json()

    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "initial configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time // 3
    event_data.event.cpu_usage = 0.05  # sample value
    event_data.event.memory_usage = 0.15  # sample value
    event_data.event.detail["url"] = f"{base_url}/api/v2/setup"
    event_data.event.detail["method"] = "POST"
    event_data.event.detail["payload"] = payload
    event_data.event.detail["headers"] = headers
    event_data.event.description = "Create admin account in InfluxDB database via HTTP endpoint"
    event_data.actor.detail["location"] = [
        "server/main.py::on_startup - line 100",
        "server/main.py::admin_account_exists - line 100",
    ]
    event_data.resources[0].detail["bucket"] = settings.INFLUXDB_USER
    event_data.resources[0].detail["organization"] = settings.INFLUXDB_ORG
    event_data.resources[0].detail["api_token"] = response["auth"]["token"]
    event_data.resources[0].detail["permissions"] = response["auth"]["permissions"]

    return event_data


def create_admin_account(username, password, organization, api_token):
    event_data: AuditRequestSchema = parse_file_as(
        type_=AuditRequestSchema,
        path="server/templates/events/rdbms-events.json",
    )

    engine = create_engine(settings.RDS_URI, echo=True)
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    logging.getLogger("sqlalchemy.engine").addHandler(handler)

    user = UserAccount(
        username=username,
        hashed_password=pwd_context.hash_plain_password(password),
        email=f"{username}@{organization.lower()}.io",
        access_key=generate_random_key(),
        api_token=api_token,
        is_active=True,
        is_superuser=True,
    )

    start_time = time()
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

    execution_time = (time() - start_time) * 1000
    sql = log_stream.getvalue()
    log_stream.close()

    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "initial configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time // 3
    event_data.event.cpu_usage = 0.25  # sample value
    event_data.event.memory_usage = 0.2  # sample value
    event_data.event.detail["sql"] = sql
    event_data.event.description = "Create admin account in PostgreSQL database"
    event_data.actor.detail["location"] = [
        "server/main.py::on_startup - line 100",
        "server/main.py::admin_account_exists - line 100",
    ]
    event_data.resources[0].detail["database"] = settings.POSTGRES_DB
    event_data.resources[0].detail["tables"] = ["accounts"]
    event_data.metadata = [
        MetadataSchema(
            is_metric=False,
            name="admin_account",
            value=user.json(),
        ),
    ]

    return event_data, user


def admin_account_exists(username: str) -> bool:
    event_data: AuditRequestSchema = parse_file_as(
        type_=AuditRequestSchema,
        path="server/templates/events/rdbms-events.json",
    )

    engine = create_engine(settings.RDS_URI, echo=True)
    session = Session(engine)

    start_time = time()
    stmt = select(UserAccount).where(UserAccount.username == username)
    user = session.exec(stmt).first()
    execution_time = (time() - start_time) * 1000
    sql = str(stmt.compile(engine, compile_kwargs={"literal_binds": True}))

    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "initial configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time // 3
    event_data.event.cpu_usage = 0.1  # sample value
    event_data.event.memory_usage = 0.1  # sample value
    event_data.event.detail["sql"] = sql
    event_data.event.description = "Check if admin account exists in PostgreSQL database"
    event_data.actor.detail["location"] = [
        "server/main.py::on_startup - line 100",
        "server/main.py::admin_account_exists - line 100",
    ]
    event_data.resources[0].detail["database"] = settings.POSTGRES_DB
    event_data.resources[0].detail["tables"] = ["accounts"]

    if user:
        event_data.metadata = [
            MetadataSchema(
                is_metric=False,
                name="admin_account",
                value=user.json(),
            ),
        ]
        return event_data, user

    return event_data, None


def create_admin_credentials():
    events = []

    host = settings.INFLUXDB_HOST
    port = settings.INFLUXDB_PORT
    user = settings.INFLUXDB_USER
    password = settings.INFLUXDB_PASSWORD
    organization = settings.INFLUXDB_ORG
    base_url = f"http://{host}:{port}"

    event_data, admin = admin_account_exists(user)
    events.append(event_data)
    if admin:
        return events, admin

    onboarding_event = influxdb_onboarding(base_url, user, password, organization)
    api_token = onboarding_event.resources[0].detail["api_token"]
    events.append(onboarding_event)

    admin_event, admin = create_admin_account(user, password, organization, api_token)
    events.append(admin_event)

    return events, admin


@app.on_event("startup")
def on_startup():
    startup_events = []

    print("Starting up...")
    event_data: AuditRequestSchema = parse_file_as(
        type_=AuditRequestSchema,
        path="server/templates/events/rdbms-events.json",
    )

    print("Creating relational database and tables...")
    start_time = time()
    sql = create_db_and_tables()
    execution_time = (time() - start_time) * 1000

    event_data.status = "success"
    event_data.level = "info"
    event_data.event.name = "app startup"
    event_data.event.type = "initial configuration"
    event_data.event.total_duration = execution_time
    event_data.event.affected_resources = 1
    event_data.event.latency = execution_time // 3
    event_data.event.cpu_usage = 0.3  # sample value
    event_data.event.memory_usage = 0.1  # sample value
    event_data.event.detail["sql"] = sql
    event_data.event.description = "Create necessary tables in PostgreSQL database"
    event_data.actor.detail["location"] = [
        "server/main.py - line 100",
        "server/database/managers.py - line 23",
    ]
    event_data.resources[0].detail["database"] = settings.POSTGRES_DB
    event_data.resources[0].detail["tables"] = ["accounts"]

    startup_events.append(event_data)
    print("Relational database and tables created!")

    print("Ping Redis server...")
    ping_redis_server()
    print("Redis server pinged!")

    admin_creation_events, admin = create_admin_credentials()
    print("Startup complete!")

    startup_events.extend(admin_creation_events)
    publish_task(admin=admin, bucket=admin.username, event_data=startup_events)


@app.get("/health", response_model=HealthResponseSchema, tags=[Tags.health_check])
async def health():
    return settings


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(audit_router)

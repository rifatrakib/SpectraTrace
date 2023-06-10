import json
import subprocess
from time import time

import requests
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, select

from server.config.factory import settings
from server.database.managers import create_db_and_tables, ping_redis_server
from server.docs.manager import read_api_metadata, read_tags_metadata
from server.events.http import create_http_event
from server.events.startup import (
    admin_account_create_event,
    check_admin_account_event,
    db_initialization_event,
    influxdb_onboarding_event,
)
from server.models.users import UserAccount
from server.routes.audit import router as audit_router
from server.routes.auth import router as auth_router
from server.routes.user import router as user_router
from server.schemas.base import HealthResponseSchema
from server.schemas.inc.audit import AuditSchema
from server.security.auth.authentication import pwd_context
from server.security.dependencies.sessions import get_influxdb_admin
from server.utils.enums import Tags
from server.utils.tasks import publish_task
from server.utils.utilities import generate_random_key

app = FastAPI(
    **read_api_metadata(),
    openapi_tags=read_tags_metadata(),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def influxdb_onboarding(base_url, user, password, organization):
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

    event_data = influxdb_onboarding_event(
        execution_time=execution_time,
        url=f"{base_url}/api/v2/setup",
        payload=payload,
        headers=headers,
        response=response,
    )
    return event_data


def create_admin_account(username, password, organization, api_token):
    engine = create_engine(settings.RDS_URI, echo=True)
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
    event_data = admin_account_create_event(
        execution_time=execution_time,
        user=user,
    )
    return event_data, user


def admin_account_exists(username: str) -> bool:
    engine = create_engine(settings.RDS_URI, echo=True)
    session = Session(engine)

    start_time = time()
    stmt = select(UserAccount).where(UserAccount.username == username)
    user = session.exec(stmt).first()
    execution_time = (time() - start_time) * 1000

    event_data = check_admin_account_event(execution_time=execution_time)
    return event_data, user


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
    api_token = onboarding_event.resource.detail["api_token"]
    events.append(onboarding_event)

    admin_event, admin = create_admin_account(user, password, organization, api_token)
    events.append(admin_event)

    return events, admin


@app.on_event("startup")
def on_startup():
    startup_events = []

    print("Starting up...")

    print("Creating relational database and tables...")
    start_time = time()
    create_db_and_tables()
    execution_time = (time() - start_time) * 1000

    event_data = db_initialization_event(execution_time=execution_time)
    startup_events.append(event_data)
    print("Relational database and tables created!")

    print("Ping Redis server...")
    ping_redis_server()
    print("Redis server pinged!")

    admin_creation_events, admin = create_admin_credentials()
    print("Startup complete!")

    startup_events.extend(admin_creation_events)
    with open("config-event.json", "r") as reader:
        startup_events.append(AuditSchema(**json.loads(reader.read())))

    publish_task(admin=admin, bucket=admin.username, event_data=startup_events)
    subprocess.run("rm config-event.json", shell=True)


@app.get("/health", response_model=HealthResponseSchema, tags=[Tags.health_check])
async def health(
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
):
    start_time = time()
    events = [
        create_http_event(
            request=request,
            status_code=200,
            affected_resource_count=0,
            execution_time=(time() - start_time) * 1000,
        ),
    ]
    publish_task(admin=admin, bucket=admin.username, event_data=events)
    return settings


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(audit_router)

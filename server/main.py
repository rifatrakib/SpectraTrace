import requests
from fastapi import FastAPI
from influxdb_client import InfluxDBClient
from sqlmodel import Session, create_engine, select

from server.config.factory import settings
from server.database.managers import create_db_and_tables, ping_redis_server
from server.docs.manager import read_api_metadata, read_tags_metadata
from server.models.users import UserAccount
from server.routes.audit import router as audit_router
from server.routes.auth import router as auth_router
from server.routes.user import router as user_router
from server.schemas.base import HealthResponseSchema
from server.security.auth.authentication import pwd_context
from server.utils.enums import Tags
from server.utils.generators import generate_random_key

app = FastAPI(
    **read_api_metadata(),
    openapi_tags=read_tags_metadata(),
)


def influxdb_onboarding(base_url, user, password, organization):
    payload = {"username": user, "password": password, "org": organization, "bucket": "test"}
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

    r = requests.post(f"{base_url}/api/v2/setup", headers=headers, json=payload)
    response = r.json()
    api_token = response["auth"]["token"]
    bucket_id = response["bucket"]["id"]

    return api_token, bucket_id


def delete_test_bucket(base_url, api_token, bucket_id):
    client = InfluxDBClient(url=base_url, token=api_token, org=settings.INFLUXDB_ORG)
    bucket_api = client.buckets_api()
    bucket_api.delete_bucket(bucket_id)
    client.close()


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

    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)


def admin_account_exists(username: str) -> bool:
    engine = create_engine(settings.RDS_URI, echo=True)
    session = Session(engine)
    user = session.exec(select(UserAccount).where(UserAccount.username == username)).first()
    if user:
        return True
    return False


def create_admin_credentials():
    host = settings.INFLUXDB_HOST
    port = settings.INFLUXDB_PORT
    user = settings.INFLUXDB_USER
    password = settings.INFLUXDB_PASSWORD
    organization = settings.INFLUXDB_ORG
    base_url = f"http://{host}:{port}"

    if admin_account_exists(user):
        return None

    api_token, bucket_id = influxdb_onboarding(base_url, user, password, organization)
    delete_test_bucket(base_url, api_token, bucket_id)
    create_admin_account(user, password, organization, api_token)


@app.on_event("startup")
def on_startup():
    print("Starting up...")

    print("Creating relational database and tables...")
    create_db_and_tables()
    print("Relational database and tables created!")

    print("Ping Redis server...")
    ping_redis_server()
    print("Redis server pinged!")

    create_admin_credentials()
    print("Startup complete!")


@app.get("/health", response_model=HealthResponseSchema, tags=[Tags.health_check])
async def health():
    return settings


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(audit_router)

from typing import Any, Dict

from influxdb_client import BucketsApi, InfluxDBClient
from sqlmodel import Session, select

from server.config.factory import settings
from server.models.users import UserAccount
from server.utils.messages import raise_404_not_found


async def check_user_access_key(session: Session, access_key: str) -> UserAccount:
    stmt = select(UserAccount).where(UserAccount.access_key == access_key)
    query = await session.execute(stmt)
    user = query.scalar()

    if not user:
        raise raise_404_not_found(message=f"User with access key {access_key} does not exist.")
    return user


async def get_admin_user(session: Session) -> UserAccount:
    stmt = select(UserAccount).where(UserAccount.username == "admin")
    query = await session.execute(stmt)
    user = query.scalar()

    if not user:
        raise raise_404_not_found(message="Admin user does not exist.")
    return user


def create_user_bucket(client: InfluxDBClient, user: Dict[str, Any]) -> str:
    with client:
        bucket_api = BucketsApi(client)
        bucket_api.create_bucket(
            bucket_name=user["username"],
            org=settings.INFLUXDB_ORG,
        )

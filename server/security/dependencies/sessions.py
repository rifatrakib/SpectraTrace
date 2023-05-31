from fastapi import Depends
from influxdb_client import InfluxDBClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from server.config.factory import settings
from server.database.audit.auth import get_admin_user
from server.models.users import UserAccount


def get_async_database_session():
    url = settings.RDS_URI_ASYNC
    engine = create_async_engine(url)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return SessionLocal()


async def get_database_session() -> AsyncSession:
    try:
        session: AsyncSession = get_async_database_session()
        yield session
    finally:
        await session.close()


async def get_influxdb_admin(session: AsyncSession = Depends(get_database_session)):
    admin: UserAccount = await get_admin_user(session=session)
    return admin


def get_influxdb_client(admin: UserAccount = Depends(get_influxdb_admin)):
    client: InfluxDBClient = InfluxDBClient(
        url=f"http://{settings.INFLUXDB_HOST}:{settings.INFLUXDB_PORT}",
        token=admin.api_token,
        org=settings.INFLUXDB_ORG,
    )

    try:
        yield client
    finally:
        client.close()

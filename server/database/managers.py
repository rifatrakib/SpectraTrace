from functools import lru_cache

from redis import Redis
from sqlmodel import create_engine

from server.config.factory import settings
from server.models.users import BaseSQLTable as UserTables


def create_db_and_tables() -> None:
    engine = create_engine(settings.RDS_URI, echo=True)
    UserTables.metadata.create_all(engine)


@lru_cache()
def get_redis_client() -> Redis:
    return Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def ping_redis_server() -> bool:
    client: Redis = get_redis_client()
    return client.ping()

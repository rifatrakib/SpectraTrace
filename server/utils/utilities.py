from functools import lru_cache
from uuid import uuid4

from pydantic import HttpUrl, parse_file_as

from server.database.managers import cache_data
from server.models.users import UserAccount
from server.schemas.inc.audit import AuditRequestSchema


def generate_random_key() -> str:
    token = str(uuid4())
    return token


def create_temporary_activation_url(user: UserAccount, url: HttpUrl) -> HttpUrl:
    key = generate_random_key()
    cache_data(key=key, data=user.json(), ttl=60)
    return f"{url}?key={key}"


@lru_cache()
def get_event_template(filename: str) -> AuditRequestSchema:
    return parse_file_as(
        type_=AuditRequestSchema,
        path=f"server/templates/events/{filename}.json",
    )

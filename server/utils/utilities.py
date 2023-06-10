from typing import Tuple
from uuid import uuid4

from pydantic import HttpUrl

from server.database.cache.ops import cache_data
from server.models.users import UserAccount
from server.schemas.inc.audit import AuditRequestSchema


def generate_random_key() -> str:
    token = str(uuid4())
    return token


def create_temporary_activation_url(user: UserAccount, url: HttpUrl) -> Tuple[HttpUrl, AuditRequestSchema]:
    key = generate_random_key()
    event = cache_data(key=key, data=user.json(), ttl=60)
    return f"{url}?key={key}", event

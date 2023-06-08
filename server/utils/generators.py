from uuid import uuid4

from pydantic import HttpUrl

from server.database.managers import cache_data
from server.models.users import UserAccount


def generate_random_key() -> str:
    token = str(uuid4())
    return token


def create_temporary_activation_url(user: UserAccount, url: HttpUrl) -> HttpUrl:
    key = generate_random_key()
    cache_data(key=key, data=user.json(), ttl=60)
    return f"{url}?key={key}"

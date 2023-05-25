import hashlib
from random import randbytes

from pydantic import HttpUrl

from server.database.managers import cache_data
from server.models.users import UserAccount


def generate_account_validation_token() -> str:
    token = randbytes(32)
    hashed_code = hashlib.sha256()
    hashed_code.update(token)
    verification_code = hashed_code.hexdigest()
    return verification_code


def create_temporary_activation_url(user: UserAccount, base_url: HttpUrl) -> HttpUrl:
    key = generate_account_validation_token()
    cache_data(key=key, data=user.json(), ttl=60)
    return f"{base_url}auth/activate/{key}"

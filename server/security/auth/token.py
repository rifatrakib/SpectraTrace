from datetime import datetime, timedelta
from typing import Union

from jose import JWTError, jwt
from pydantic import ValidationError

from server.config.factory import settings
from server.models.users import UserAccount
from server.schemas.out.auth import TokenData, TokenUser


def create_jwt(data: UserAccount, expires_delta: Union[datetime, None] = None) -> str:
    expires_delta = expires_delta if expires_delta else timedelta(minutes=settings.JWT_MIN)
    expire = datetime.utcnow() + expires_delta
    to_encode = TokenData(**data.dict(), exp=expire, sub=settings.JWT_SUBJECT)
    return jwt.encode(
        to_encode.dict(),
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_jwt(token: str) -> TokenUser:
    try:
        payload = jwt.decode(
            token=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_data = TokenUser(
            id=payload.get("id"),
            username=payload.get("username"),
            email=payload.get("email"),
            is_active=payload.get("is_active"),
        )
    except JWTError as token_decode_error:
        raise ValueError("unable to decode JWT") from token_decode_error
    except ValidationError as validation_error:
        raise ValueError("invalid payload in JWT") from validation_error
    return user_data

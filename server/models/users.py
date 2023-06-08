from typing import Union

from pydantic import EmailStr
from sqlmodel import Field

from server.models.base import BaseSQLTable


class UserAccount(BaseSQLTable, table=True):
    __tablename__ = "accounts"

    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str = Field(...)
    access_key: str = Field(min_length=36, max_length=36, index=True, unique=True)
    api_token: Union[str, None] = Field(default=None, nullable=True, index=True, unique=True)
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)

from sqlmodel import Field

from server.models.base import BaseSQLTable


class UserAccount(BaseSQLTable, table=True):
    __tablename__ = "accounts"

    username: str = Field(..., index=True, unique=True)
    email: str = Field(..., index=True, unique=True)
    hashed_password: str = Field(...)
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)

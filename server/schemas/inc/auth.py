from pydantic import Field

from server.schemas.base import BaseRequestSchema
from server.schemas.common.users import UserBase


class SignupRequestSchema(BaseRequestSchema, UserBase):
    password: str = Field(
        title="password",
        decription="""
            Password containing at least 1 uppercase letter, 1 lowercase letter,
            1 number, 1 character that is neither letter nor number, and
            between 8 to 64 characters.
        """,
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,64}$",
        min_length=8,
        max_length=64,
    )


class LoginRequestSchema(BaseRequestSchema):
    username: str = Field(
        title="username",
        description="Username of the user to login.",
        min_length=1,
        max_length=64,
    )
    password: str = Field(
        title="password",
        description="Password of the user to login.",
        min_length=1,
        max_length=64,
    )

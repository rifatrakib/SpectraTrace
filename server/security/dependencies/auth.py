from typing import Any, Dict, Type

from fastapi import Depends, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr

from server.schemas.inc.auth import LoginRequestSchema, PasswordChangeRequestSchema, SignupRequestSchema
from server.schemas.out.auth import TokenUser
from server.security.auth.token import decode_jwt
from server.utils.messages import raise_403_forbidden, raise_422_unprocessable_entity

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def extract_options(
    model: Type[BaseModel],
    field: str,
    updates: Dict[str, Any] = {},
) -> Dict[str, Any]:
    options = model.schema()["properties"][field]
    options.update(updates)
    return options


async def decode_user_token(
    token: str = Depends(oauth2_scheme),
) -> TokenUser:
    try:
        user_data: TokenUser = decode_jwt(token)
        return user_data
    except ValueError:
        raise raise_403_forbidden(
            message="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def is_user_active(
    user: TokenUser = Depends(decode_user_token),
):
    if not user.is_active:
        raise raise_403_forbidden(message="Inactive user")
    return user


def username_input_field(
    username: str = Form(
        title="Username",
        decription="""
            Unique username containing letters, numbers, and
            any of (., _, -, @) in between 5 to 32 characters.
        """.replace("\n", " ").strip(),
        regex=r"^[\w.@_-]{5,32}$",
        min_length=5,
        max_length=32,
        example="admin",
    ),
) -> str:
    return username


def email_input_field(
    email: EmailStr = Form(
        title="Email",
        decription="Unique email that can be used for user account activation.",
        example="admin@spectratrace.io",
    ),
) -> EmailStr:
    return email


def password_input_field(
    password: str = Form(
        alias="password",
        title="Password",
        decription="""
            Password containing at least 1 uppercase letter, 1 lowercase letter,
            1 number, 1 character that is neither letter nor number, and
            between 8 to 64 characters.
        """.replace("\n", " ").strip(),
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,64}$",
        min_length=8,
        max_length=64,
        example="Admin@12345",
    ),
) -> str:
    return password


def repeat_password_input_field(
    repeat_password: str = Form(
        alias="repeatPassword",
        title="Repeat password",
        description="Repeat password to confirm password.",
        example="Admin@12345",
    ),
) -> str:
    return repeat_password


def new_password_input_field(
    new_password: str = Form(
        alias="newPassword",
        title="New password",
        decription="""
            Password containing at least 1 uppercase letter, 1 lowercase letter,
            1 number, 1 character that is neither letter nor number, and
            between 8 to 64 characters.
        """.replace("\n", " ").strip(),
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,64}$",
        min_length=8,
        max_length=64,
        example="Admin@12345",
    )
) -> str:
    return new_password


def signup_request_form(
    username: str = Depends(username_input_field),
    email: str = Depends(email_input_field),
    password: str = Depends(password_input_field),
    repeat_password: str = Depends(repeat_password_input_field),
):
    if password != repeat_password:
        raise raise_422_unprocessable_entity("Passwords do not match.")
    return SignupRequestSchema(username=username, email=email, password=password)


def login_request_form(
    username: str = Depends(username_input_field),
    password: str = Depends(password_input_field),
):
    return LoginRequestSchema(username=username, password=password)


def password_change_request_form(
    current_password: str = Depends(password_input_field),
    new_password: str = Depends(new_password_input_field),
    repeat_password: str = Depends(repeat_password_input_field),
):
    if new_password != repeat_password:
        raise raise_422_unprocessable_entity("Passwords do not match.")
    return PasswordChangeRequestSchema(current_password=current_password, new_password=new_password)


def password_reset_request_form(
    new_password: str = Depends(new_password_input_field),
    repeat_password: str = Depends(repeat_password_input_field),
) -> str:
    if new_password != repeat_password:
        raise raise_422_unprocessable_entity("Passwords do not match.")
    return new_password

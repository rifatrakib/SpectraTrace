from typing import Any, Dict, Type

from fastapi import Depends, Form
from pydantic import BaseModel

from server.schemas.inc.auth import LoginRequestSchema, SignupRequestSchema
from server.utils.messages import raise_422_unprocessable_entity


def extract_schema_from_model(
    model: Type[BaseModel],
    field: str,
    updates: Dict[str, Any] = {},
) -> Dict[str, Any]:
    options = model.schema()["properties"][field]
    options.update(updates)
    return options


def username_form_input(username: str = Form(**extract_schema_from_model(SignupRequestSchema, "username"))):
    return username


def email_form_input(email: str = Form(**extract_schema_from_model(SignupRequestSchema, "email"))):
    return email


def password_form_input(password: str = Form(**extract_schema_from_model(SignupRequestSchema, "password"))):
    return password


def repeat_password_form_input(
    repeat_password: str = Form(
        **extract_schema_from_model(SignupRequestSchema, "password", {"alias": "repeatPassword"}),
    ),
):
    return repeat_password


def signup_request_form(
    username: str = Depends(username_form_input),
    email: str = Depends(email_form_input),
    password: str = Depends(password_form_input),
    repeat_password: str = Depends(repeat_password_form_input),
):
    if password != repeat_password:
        raise raise_422_unprocessable_entity("Passwords do not match.")
    return SignupRequestSchema(username=username, email=email, password=password)


def login_request_form(
    username: str = Depends(username_form_input),
    password: str = Depends(password_form_input),
):
    return LoginRequestSchema(username=username, password=password)

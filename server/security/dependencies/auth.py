from typing import Any, Dict, Type

from fastapi import Depends, Form
from pydantic import BaseModel
from sqlmodel import Session, create_engine

from server.config.factory import settings
from server.schemas.inc.auth import LoginRequestSchema, SignupRequestSchema


def get_database_session() -> Session:
    engine = create_engine(settings.RDS_URI, echo=True)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def extract_schema_from_model(model: Type[BaseModel], field: str) -> Dict[str, Any]:
    return model.schema()["properties"][field]


def username_form_input(username: str = Form(**extract_schema_from_model(SignupRequestSchema, "username"))):
    return username


def email_form_input(email: str = Form(**extract_schema_from_model(SignupRequestSchema, "email"))):
    return email


def password_form_input(password: str = Form(**extract_schema_from_model(SignupRequestSchema, "password"))):
    return password


def signup_request_form(
    username: str = Depends(username_form_input),
    email: str = Depends(email_form_input),
    password: str = Depends(password_form_input),
):
    return SignupRequestSchema(username=username, email=email, password=password)


def login_request_form(
    username: str = Depends(username_form_input),
    password: str = Depends(password_form_input),
):
    return LoginRequestSchema(username=username, password=password)

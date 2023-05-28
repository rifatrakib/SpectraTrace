from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import EmailStr
from sqlmodel import Session

from server.database.managers import activate_from_cache, is_in_cache
from server.database.users.auth import (
    activate_user_account,
    authenticate_user,
    create_user_account,
    read_user_by_email,
    reset_user_password,
    update_password,
)
from server.schemas.base import MessageResponseSchema
from server.schemas.inc.auth import LoginRequestSchema, PasswordChangeRequestSchema, SignupRequestSchema
from server.schemas.out.auth import TokenResponseSchema, TokenUser
from server.security.auth.token import create_jwt
from server.security.dependencies.auth import (
    email_input_field,
    is_user_active,
    login_request_form,
    password_change_request_form,
    password_reset_request_form,
    signup_request_form,
)
from server.security.dependencies.sessions import get_database_session
from server.utils.enums import Tags
from server.utils.generators import create_temporary_activation_url
from server.utils.messages import raise_410_gone

router = APIRouter(prefix="/auth", tags=[Tags.authentication])


@router.post(
    "/signup",
    summary="Register new user",
    description="Register a new user account.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: Request,
    payload: SignupRequestSchema = Depends(signup_request_form),
    session: Session = Depends(get_database_session),
) -> MessageResponseSchema:
    try:
        new_user = create_user_account(session=session, payload=payload)
        url = create_temporary_activation_url(new_user, f"{request.base_url}auth/activate")
        return {"msg": f"Account created. Activate your account using {url}."}
    except HTTPException as e:
        raise e


@router.post(
    "/login",
    summary="Authenticate user",
    description="Authenticate a user account.",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def login(
    payload: LoginRequestSchema = Depends(login_request_form),
    session: Session = Depends(get_database_session),
) -> TokenResponseSchema:
    try:
        user = authenticate_user(
            session=session,
            username=payload.username,
            password=payload.password,
        )
        token = create_jwt(user)
        return {"access_token": token, "token_type": "Bearer"}
    except HTTPException as e:
        raise e


@router.get(
    "/activate",
    summary="Activate user account",
    description="Activate a user account.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def activate_account(
    key: str = Query(description="Activation key."),
    session: Session = Depends(get_database_session),
) -> MessageResponseSchema:
    try:
        user = activate_from_cache(key=key)
        updated_user = activate_user_account(session=session, user_id=user["id"])
        return {"msg": f"User account {updated_user.username} activated."}
    except HTTPException as e:
        raise e


@router.post(
    "/activate/resend",
    summary="Resend activation key",
    description="Resend activation key to a user.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def resend_activation_key(
    request: Request,
    email: EmailStr = Depends(email_input_field),
    session: Session = Depends(get_database_session),
) -> MessageResponseSchema:
    try:
        user = read_user_by_email(session=session, email=email)
        url = create_temporary_activation_url(user, f"{request.base_url}auth/activate")
        return {"msg": f"Activation key resent. Activate your account using {url}."}
    except HTTPException as e:
        raise e


@router.patch(
    "/password/change",
    summary="Change user password",
    description="Change a user's password.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    user: TokenUser = Depends(is_user_active),
    payload: PasswordChangeRequestSchema = Depends(password_change_request_form),
    session: Session = Depends(get_database_session),
):
    try:
        user = update_password(session=session, user_id=user.id, payload=payload)
        return {"msg": "Password changed."}
    except HTTPException as e:
        raise e


@router.post(
    "/password/forgot",
    summary="Forgot password",
    description="Send password reset link to user.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    request: Request,
    email: EmailStr = Depends(email_input_field),
    session: Session = Depends(get_database_session),
) -> MessageResponseSchema:
    try:
        user = read_user_by_email(session=session, email=email)
        url = create_temporary_activation_url(user, f"{request.base_url}auth/password/reset")
        return {"msg": f"Activation key resent. Activate your account using {url}."}
    except HTTPException as e:
        raise e


@router.get(
    "/password/reset",
    summary="Reset password",
    description="Reset a user's password.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def is_reset_password_route_valid(key: str = Query(description="Activation key.")) -> MessageResponseSchema:
    try:
        if is_in_cache(key=key):
            return {"msg": "Allowed to reset password."}
        raise raise_410_gone(message="Token expired or invalid.")
    except HTTPException as e:
        raise e


@router.patch(
    "/password/reset",
    summary="Reset password",
    description="Reset a user's password.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    key: str = Query(description="Activation key."),
    session: Session = Depends(get_database_session),
    new_password: str = Depends(password_reset_request_form),
) -> MessageResponseSchema:
    try:
        user = activate_from_cache(key=key)
        updated_user = reset_user_password(session=session, user_id=user["id"], new_password=new_password)
        return {"msg": f"User account {updated_user.username} reset password successful."}
    except HTTPException as e:
        raise e

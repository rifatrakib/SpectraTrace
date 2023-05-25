from fastapi import APIRouter, HTTPException, Request, status

from server.database.managers import activate_from_cache
from server.database.users.auth import (
    activate_user_account,
    authenticate_user,
    create_user_account,
    read_user_by_username,
)
from server.schemas.base import MessageResponseSchema
from server.schemas.inc.auth import LoginRequestSchema, SignupRequestSchema
from server.schemas.out.auth import TokenResponseSchema
from server.security.token import create_jwt
from server.utils.enums import Tags
from server.utils.generators import create_temporary_activation_url

router = APIRouter(prefix="/auth", tags=[Tags.authentication])


@router.post(
    "/signup",
    summary="Register new user",
    description="Register a new user account.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: SignupRequestSchema, request: Request) -> MessageResponseSchema:
    try:
        new_user = create_user_account(payload)
        url = create_temporary_activation_url(new_user, request.base_url)
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
async def login(payload: LoginRequestSchema) -> TokenResponseSchema:
    try:
        user = authenticate_user(payload.username, payload.password)
        token = create_jwt(user)
        return {"access_token": token, "token_type": "Bearer"}
    except HTTPException as e:
        raise e


@router.get(
    "/activate/{token}",
    summary="Activate user account",
    description="Activate a user account.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def activate_account(token: str) -> MessageResponseSchema:
    try:
        user = activate_from_cache(key=token)
        updated_user = activate_user_account(user["id"])
        return {"msg": f"User account {updated_user.username} activated."}
    except HTTPException as e:
        raise e


@router.get(
    "/activate/{username}/resend",
    summary="Resend activation key",
    description="Resend activation key to a user.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def resend_activation_key(username: str, request: Request) -> MessageResponseSchema:
    try:
        user = read_user_by_username(username)
        url = create_temporary_activation_url(user, request.base_url)
        return {"msg": f"Activation key resent. Activate your account using {url}."}
    except HTTPException as e:
        raise e
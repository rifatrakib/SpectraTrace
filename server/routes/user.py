from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import EmailStr
from sqlmodel import Session

from server.database.managers import activate_from_cache
from server.database.users.user import read_user_by_id, update_user_access_key
from server.schemas.base import MessageResponseSchema
from server.schemas.out.auth import TokenUser
from server.schemas.out.user import UserAccessKeyResponseSchema, UserResponseSchema
from server.security.dependencies.auth import email_input_field, is_user_active
from server.security.dependencies.sessions import get_database_session
from server.utils.enums import Tags
from server.utils.generators import create_temporary_activation_url
from server.utils.messages import raise_400_bad_request

router = APIRouter(
    prefix="/users",
    tags=[Tags.user],
    dependencies=[Depends(is_user_active)],
)


@router.get(
    "/me",
    summary="Get current user",
    description="Get current user",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def read_current_user(
    current_user: TokenUser = Depends(is_user_active),
    session: Session = Depends(get_database_session),
):
    try:
        user = read_user_by_id(session=session, user_id=current_user.id)
        return user
    except HTTPException as e:
        raise e


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description="Get user by ID",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def read_single_user(
    user_id: int,
    session: Session = Depends(get_database_session),
):
    try:
        user = read_user_by_id(session=session, user_id=user_id)
        return user
    except HTTPException as e:
        raise e


@router.get(
    "/access-key/me",
    summary="Get current user access key",
    description="Get current user access key",
    response_model=UserAccessKeyResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def read_current_user_access_key(
    current_user: TokenUser = Depends(is_user_active),
    session: Session = Depends(get_database_session),
):
    try:
        user = read_user_by_id(session=session, user_id=current_user.id)
        return user
    except HTTPException as e:
        raise e


@router.post(
    "/access-key/forgot",
    summary="Forgot user access key",
    description="Forgot user access key",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def forgot_user_access_key(
    request: Request,
    current_user: TokenUser = Depends(is_user_active),
    email: EmailStr = Depends(email_input_field),
):
    try:
        if current_user.email != email:
            raise raise_400_bad_request(message="Provided wrong email.")
        url = create_temporary_activation_url(current_user, f"{request.base_url}users/access-key/reset")
        return {"msg": f"Reset your access key using {url}."}
    except HTTPException as e:
        raise e


@router.get(
    "/access-key/reset",
    summary="Reset user access key",
    description="Reset user access key",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def reset_user_access_key(
    key: str = Query(description="Activation key."),
    session: Session = Depends(get_database_session),
):
    try:
        user = activate_from_cache(key=key)
        updated_user = update_user_access_key(session=session, user_id=user["id"])
        return {"msg": f"User account {updated_user.username} reset access key successful."}
    except HTTPException as e:
        raise e

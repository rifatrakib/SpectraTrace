from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from server.database.users.user import read_user_by_id
from server.schemas.out.auth import TokenUser
from server.schemas.out.user import UserResponseSchema
from server.security.dependencies.auth import is_user_active
from server.security.dependencies.sessions import get_database_session
from server.utils.enums import Tags

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
async def read_current_user(current_user: TokenUser = Depends(is_user_active)):
    return current_user


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

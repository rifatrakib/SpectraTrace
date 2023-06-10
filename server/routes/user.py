from time import time

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.database.users.user import read_user_by_id
from server.events.http import create_http_event
from server.models.users import UserAccount
from server.schemas.out.auth import TokenUser
from server.schemas.out.user import UserAccessKeyResponseSchema, UserResponseSchema
from server.security.dependencies.auth import is_user_active
from server.security.dependencies.sessions import get_database_session, get_influxdb_admin
from server.utils.enums import Tags
from server.utils.tasks import publish_task

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
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
    current_user: TokenUser = Depends(is_user_active),
    session: AsyncSession = Depends(get_database_session),
) -> UserResponseSchema:
    status_code = 200
    events = []
    start_time = time()
    try:
        user, event = await read_user_by_id(session=session, user_id=current_user.id)
        events.append(event)
        return user
    except HTTPException as e:
        status_code = e.status_code
        raise e
    finally:
        events.append(
            create_http_event(
                request=request,
                status_code=status_code,
                affected_resource_count=len(events),
                execution_time=(time() - start_time) * 1000,
            ),
        )
        publish_task(admin=admin, bucket=admin.username, event_data=events)


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description="Get user by ID",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def read_single_user(
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
    user_id: int = Path(title="User ID", description="User ID"),
    session: AsyncSession = Depends(get_database_session),
) -> UserResponseSchema:
    status_code = 200
    events = []
    start_time = time()

    try:
        user, event = await read_user_by_id(session=session, user_id=user_id)
        events.append(event)
        return user
    except HTTPException as e:
        status_code = e.status_code
        raise e
    finally:
        events.append(
            create_http_event(
                request=request,
                status_code=status_code,
                affected_resource_count=len(events),
                execution_time=(time() - start_time) * 1000,
            ),
        )
        publish_task(admin=admin, bucket=admin.username, event_data=events)


@router.get(
    "/access-key/me",
    summary="Get current user access key",
    description="Get current user access key",
    response_model=UserAccessKeyResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def read_current_user_access_key(
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
    current_user: TokenUser = Depends(is_user_active),
    session: AsyncSession = Depends(get_database_session),
) -> UserAccessKeyResponseSchema:
    status_code = 200
    events = []
    start_time = time()

    try:
        user, event = await read_user_by_id(session=session, user_id=current_user.id)
        events.append(event)
        return user
    except HTTPException as e:
        status_code = e.status_code
        raise e
    finally:
        events.append(
            create_http_event(
                request=request,
                status_code=status_code,
                affected_resource_count=len(events),
                execution_time=(time() - start_time) * 1000,
            ),
        )
        publish_task(admin=admin, bucket=admin.username, event_data=events)

from time import time

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from influxdb_client import InfluxDBClient
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from server.database.audit.auth import create_user_bucket
from server.database.cache.ops import activate_from_cache, is_in_cache
from server.database.users.auth import (
    activate_user_account,
    authenticate_user,
    create_user_account,
    read_user_by_email,
    reset_user_password,
    update_password,
)
from server.events.http import create_http_event
from server.models.users import UserAccount
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
from server.security.dependencies.sessions import get_database_session, get_influxdb_admin, get_influxdb_client
from server.utils.enums import Tags
from server.utils.messages import raise_410_gone
from server.utils.tasks import publish_task
from server.utils.utilities import create_temporary_activation_url

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
    admin: UserAccount = Depends(get_influxdb_admin),
    payload: SignupRequestSchema = Depends(signup_request_form),
    session: AsyncSession = Depends(get_database_session),
) -> MessageResponseSchema:
    status_code = 201
    events = []
    start_time = time()

    try:
        new_user, event = await create_user_account(
            session=session,
            payload=payload,
        )
        events.append(event)

        url, event = create_temporary_activation_url(new_user, f"{request.base_url}auth/activate")
        events.append(event)

        return {"msg": f"Account created. Activate your account using {url}."}
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


@router.post(
    "/login",
    summary="Authenticate user",
    description="Authenticate a user account.",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def login(
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
    payload: LoginRequestSchema = Depends(login_request_form),
    session: AsyncSession = Depends(get_database_session),
) -> TokenResponseSchema:
    status_code = 202
    events = []
    start_time = time()

    try:
        user, event = await authenticate_user(
            session=session,
            username=payload.username,
            password=payload.password,
        )
        events.append(event)

        token = create_jwt(user)
        return {"access_token": token, "token_type": "Bearer"}
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
            )
        )
        publish_task(admin=admin, bucket=admin.username, event_data=events)


@router.get(
    "/activate",
    summary="Activate user account",
    description="Activate a user account.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def activate_account(
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
    key: str = Query(description="Activation key."),
    session: AsyncSession = Depends(get_database_session),
    influx_client: InfluxDBClient = Depends(get_influxdb_client),
) -> MessageResponseSchema:
    status_code = 200
    events = []
    start_time = time()

    try:
        user, cache_events = activate_from_cache(key=key)
        events.extend(cache_events)

        event = create_user_bucket(client=influx_client, user=user)
        events.append(event)

        updated_user, event = await activate_user_account(session=session, user_id=user["id"])
        events.append(event)

        return {"msg": f"User account {updated_user.username} activated."}
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


@router.post(
    "/activate/resend",
    summary="Resend activation key",
    description="Resend activation key to a user.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def resend_activation_key(
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
    email: EmailStr = Depends(email_input_field),
    session: AsyncSession = Depends(get_database_session),
) -> MessageResponseSchema:
    status_code = 200
    events = []
    start_time = time()

    try:
        user, event = await read_user_by_email(session=session, email=email)
        events.append(event)

        url, event = create_temporary_activation_url(user, f"{request.base_url}auth/activate")
        events.append(event)

        return {"msg": f"Activation key resent. Activate your account using {url}."}
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
            )
        )
        publish_task(admin=admin, bucket=admin.username, event_data=events)


@router.patch(
    "/password/change",
    summary="Change user password",
    description="Change a user's password.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
    user: TokenUser = Depends(is_user_active),
    payload: PasswordChangeRequestSchema = Depends(password_change_request_form),
    session: AsyncSession = Depends(get_database_session),
) -> MessageResponseSchema:
    status_code = 200
    events = []
    start_time = time()

    try:
        user, event = await update_password(session=session, user_id=user.id, payload=payload)
        events.append(event)

        return {"msg": "Password changed."}
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
            )
        )
        publish_task(admin=admin, bucket=admin.username, event_data=events)


@router.post(
    "/password/forgot",
    summary="Forgot password",
    description="Send password reset link to user.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
    email: EmailStr = Depends(email_input_field),
    session: AsyncSession = Depends(get_database_session),
) -> MessageResponseSchema:
    status_code = 200
    events = []
    start_time = time()

    try:
        user, event = await read_user_by_email(session=session, email=email)
        events.append(event)

        url, event = create_temporary_activation_url(user, f"{request.base_url}auth/password/reset")
        events.append(event)

        return {"msg": f"Activation key resent. Activate your account using {url}."}
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
            )
        )
        publish_task(admin=admin, bucket=admin.username, event_data=events)


@router.get(
    "/password/reset",
    summary="Reset password",
    description="Reset a user's password.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def is_reset_password_route_valid(
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
    key: str = Query(description="Activation key."),
) -> MessageResponseSchema:
    status_code = 200
    events = []
    start_time = time()

    try:
        is_valid, event = is_in_cache(key=key)
        events.append(event)

        if is_valid:
            return {"msg": "Allowed to reset password."}
        raise raise_410_gone(message="Token expired or invalid.")
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


@router.patch(
    "/password/reset",
    summary="Reset password",
    description="Reset a user's password.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    request: Request,
    admin: UserAccount = Depends(get_influxdb_admin),
    key: str = Query(description="Activation key."),
    session: AsyncSession = Depends(get_database_session),
    new_password: str = Depends(password_reset_request_form),
) -> MessageResponseSchema:
    status_code = 200
    events = []
    start_time = time()

    try:
        user, cache_events = activate_from_cache(key=key)
        events.extend(cache_events)

        updated_user, event = await reset_user_password(
            session=session,
            user_id=user["id"],
            new_password=new_password,
        )
        events.append(event)

        return {"msg": f"User account {updated_user.username} reset password successful."}
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
            )
        )
        publish_task(admin=admin, bucket=admin.username, event_data=events)

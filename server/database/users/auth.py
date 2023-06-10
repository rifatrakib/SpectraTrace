from time import time
from typing import Tuple

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import or_, select

from server.events.rds import relational_db_event
from server.models.users import UserAccount
from server.schemas.inc.audit import AuditRequestSchema
from server.schemas.inc.auth import PasswordChangeRequestSchema, SignupRequestSchema
from server.security.auth.authentication import pwd_context
from server.utils.messages import (
    raise_400_bad_request,
    raise_401_unauthorized,
    raise_403_forbidden,
    raise_404_not_found,
)
from server.utils.utilities import generate_random_key


async def read_user_by_email_or_username(
    session: AsyncSession,
    username: str,
    email: EmailStr,
) -> UserAccount:
    stmt = select(UserAccount).where(or_(UserAccount.username == username, UserAccount.email == email))
    query = await session.execute(stmt)
    user = query.scalar()
    return user


async def create_user_account(
    session: AsyncSession,
    payload: SignupRequestSchema,
) -> Tuple[UserAccount, AuditRequestSchema]:
    start_time = time()
    user = await read_user_by_email_or_username(
        session=session,
        username=payload.username,
        email=payload.email,
    )

    if user:
        if user.username == payload.username:
            raise raise_400_bad_request(message=f"The username {payload.username} is already registered.")
        if user.email == payload.email:
            raise raise_400_bad_request(message=f"The email {payload.email} is already registered.")

    hashed_password = pwd_context.hash_plain_password(payload.password)
    user = UserAccount(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password,
        access_key=generate_random_key(),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    event = relational_db_event(
        execution_time=(time() - start_time) * 1000,
        affected_resource_count=1,
        user=user,
        event_method="write",
        event_name="user-account-created",
        event_type="insert",
        event_description=f"User account for {user.username} was created",
    )

    return user, event


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> Tuple[UserAccount, AuditRequestSchema]:
    start_time = time()
    stmt = select(UserAccount).where(UserAccount.username == username)
    query = await session.execute(stmt)
    user = query.scalar()

    if not user:
        raise raise_404_not_found(message=f"The username {username} is not registered.")

    if not user.is_active:
        raise raise_403_forbidden(message=f"The account for username {username} is not activated.")

    if not pwd_context.verify_password(password, user.hashed_password):
        raise raise_401_unauthorized(message="Incorrect password.")

    event = relational_db_event(
        execution_time=(time() - start_time) * 1000,
        affected_resource_count=1,
        user=user,
        event_method="read",
        event_name="user-authenticated",
        event_type="select",
        event_description=f"User {user.username} was authenticated",
    )

    return user, event


async def activate_user_account(
    session: AsyncSession,
    user_id: int,
) -> Tuple[UserAccount, AuditRequestSchema]:
    start_time = time()
    stmt = select(UserAccount).where(UserAccount.id == user_id)
    query = await session.execute(stmt)
    user = query.scalar()

    user.is_active = True
    session.add(user)
    await session.commit()
    await session.refresh(user)

    event = relational_db_event(
        execution_time=(time() - start_time) * 1000,
        affected_resource_count=1,
        user=user,
        event_method="write",
        event_name="user-account-activated",
        event_type="update",
        event_description=f"User account for {user.username} was activated",
    )

    return user, event


async def read_user_by_email(
    session: AsyncSession,
    email: EmailStr,
) -> Tuple[UserAccount, AuditRequestSchema]:
    start_time = time()
    stmt = select(UserAccount).where(UserAccount.email == email)
    query = await session.execute(stmt)
    user = query.scalar()

    if not user:
        raise raise_404_not_found(message=f"{email} is not registered.")

    event = relational_db_event(
        execution_time=(time() - start_time) * 1000,
        affected_resource_count=1,
        user=user,
        event_method="read",
        event_name="user-account-read",
        event_type="select",
        event_description=f"User account for {user.username} was read",
    )

    return user, event


async def update_password(
    session: AsyncSession,
    user_id: int,
    payload: PasswordChangeRequestSchema,
) -> Tuple[UserAccount, AuditRequestSchema]:
    start_time = time()
    stmt = select(UserAccount).where(UserAccount.id == user_id)
    query = await session.execute(stmt)
    user = query.scalar()

    if not pwd_context.verify_password(payload.current_password, user.hashed_password):
        raise raise_401_unauthorized(message="Incorrect password.")

    user.hashed_password = pwd_context.hash_plain_password(payload.new_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    event = relational_db_event(
        execution_time=(time() - start_time) * 1000,
        affected_resource_count=1,
        user=user,
        event_method="write",
        event_name="user-password-updated",
        event_type="update",
        event_description=f"User password for {user.username} was updated",
    )

    return user, event


async def reset_user_password(
    session: AsyncSession,
    user_id: int,
    new_password: str,
) -> Tuple[UserAccount, AuditRequestSchema]:
    start_time = time()
    stmt = select(UserAccount).where(UserAccount.id == user_id)
    query = await session.execute(stmt)
    user = query.scalar()

    user.hashed_password = pwd_context.hash_plain_password(new_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    event = relational_db_event(
        execution_time=(time() - start_time) * 1000,
        affected_resource_count=1,
        user=user,
        event_method="write",
        event_name="user-password-reset",
        event_type="update",
        event_description=f"User password for {user.username} was reset",
    )

    return user, event

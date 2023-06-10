from time import time
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from server.events.rds import relational_db_event
from server.models.users import UserAccount
from server.schemas.inc.audit import AuditRequestSchema
from server.utils.messages import raise_404_not_found


async def read_user_by_id(
    session: AsyncSession,
    user_id: int,
) -> Tuple[UserAccount, AuditRequestSchema]:
    start_time = time()
    stmt = select(UserAccount).where(UserAccount.id == user_id)
    query = await session.execute(stmt)
    user = query.scalar()

    if not user:
        raise raise_404_not_found(message=f"User with ID {user_id} does not exist.")

    event = relational_db_event(
        execution_time=(time() - start_time) * 1000,
        affected_resource_count=1,
        user=user,
        event_method="read",
        event_name="user-read",
        event_type="select",
        event_description=f"Read user with ID {user_id}",
    )

    return user, event

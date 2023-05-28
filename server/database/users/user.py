from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from server.models.users import UserAccount
from server.utils.generators import generate_random_key
from server.utils.messages import raise_404_not_found


async def read_user_by_id(session: AsyncSession, user_id: int) -> UserAccount:
    stmt = select(UserAccount).where(UserAccount.id == user_id)
    query = await session.execute(stmt)
    user = query.scalar()

    if not user:
        raise raise_404_not_found(message=f"User with ID {user_id} does not exist.")
    return user


async def update_user_access_key(session: AsyncSession, user_id: int) -> UserAccount:
    stmt = select(UserAccount).where(UserAccount.id == user_id)
    query = await session.execute(stmt)
    user = query.scalar()
    user.access_key = generate_random_key()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

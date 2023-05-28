from sqlmodel import Session, select

from server.models.users import UserAccount
from server.utils.generators import generate_random_key
from server.utils.messages import raise_404_not_found


def read_user_by_id(session: Session, user_id: int) -> UserAccount:
    user = session.exec(select(UserAccount).where(UserAccount.id == user_id)).first()
    if not user:
        raise raise_404_not_found(message=f"User with ID {user_id} does not exist.")
    return user


def update_user_access_key(session: Session, user_id: int) -> UserAccount:
    user = read_user_by_id(session=session, user_id=user_id)
    user.access_key = generate_random_key()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

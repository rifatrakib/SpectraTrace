from sqlmodel import Session, select

from server.models.users import UserAccount
from server.utils.messages import raise_404_not_found


def read_user_by_id(session: Session, user_id: int) -> UserAccount:
    user = session.exec(select(UserAccount).where(UserAccount.id == user_id)).first()
    if not user:
        raise raise_404_not_found(message=f"User with ID {user_id} does not exist.")
    return user

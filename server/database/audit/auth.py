from sqlmodel import Session, select

from server.models.users import UserAccount
from server.utils.messages import raise_404_not_found


def check_user_access_key(session: Session, access_key: str) -> UserAccount:
    user = session.exec(select(UserAccount).where(UserAccount.access_key == access_key)).first()
    if not user:
        raise raise_404_not_found(message=f"User with access key {access_key} does not exist.")
    return user

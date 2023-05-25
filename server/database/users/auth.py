from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from server.models.users import UserAccount
from server.schemas.inc.auth import PasswordChangeRequestSchema, SignupRequestSchema
from server.security.auth.authentication import pwd_context
from server.utils.generators import generate_random_key
from server.utils.messages import (
    raise_400_bad_request,
    raise_401_unauthorized,
    raise_403_forbidden,
    raise_404_not_found,
)


def create_user_account(session: Session, payload: SignupRequestSchema) -> UserAccount:
    hashed_password = pwd_context.hash_plain_password(payload.password)
    user = UserAccount(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password,
        access_key=generate_random_key(),
    )

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError:
        raise raise_400_bad_request(message=f"The username {payload.username} is already registered.")


def authenticate_user(session: Session, username: str, password: str) -> UserAccount:
    user = session.exec(select(UserAccount).where(UserAccount.username == username)).first()

    if not user:
        raise raise_404_not_found(message=f"The username {username} is not registered.")

    if not user.is_active:
        raise raise_403_forbidden(message=f"The account for username {username} is not activated.")

    if not pwd_context.verify_password(password, user.hashed_password):
        raise raise_401_unauthorized(message="Incorrect password.")

    return user


def activate_user_account(session: Session, user_id: int) -> UserAccount:
    user = session.get(UserAccount, user_id)
    user.is_active = True
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def read_user_by_email(session: Session, email: EmailStr) -> UserAccount:
    user = session.exec(select(UserAccount).where(UserAccount.email == email)).first()
    if not user:
        raise raise_404_not_found(message=f"{email} is not registered.")
    return user


def update_password(
    session: Session,
    user_id: int,
    payload: PasswordChangeRequestSchema,
) -> UserAccount:
    user = session.get(UserAccount, user_id)

    if not pwd_context.verify_password(payload.current_password, user.hashed_password):
        raise raise_401_unauthorized(message="Incorrect password.")

    user.hashed_password = pwd_context.hash_plain_password(payload.new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def reset_user_password(session: Session, user_id: int, new_password: str) -> UserAccount:
    user = session.get(UserAccount, user_id)
    user.hashed_password = pwd_context.hash_plain_password(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

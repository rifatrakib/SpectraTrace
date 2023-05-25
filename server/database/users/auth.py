from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, create_engine, select

from server.config.factory import settings
from server.models.users import UserAccount
from server.schemas.inc.auth import SignupRequestSchema
from server.security.authentication import pwd_context
from server.utils.generators import generate_random_key
from server.utils.messages import (
    raise_400_bad_request,
    raise_401_unauthorized,
    raise_403_forbidden,
    raise_404_not_found,
)


def create_user_account(payload: SignupRequestSchema) -> UserAccount:
    engine = create_engine(settings.RDS_URI, echo=True)
    hashed_password = pwd_context.hash_plain_password(payload.password)
    user = UserAccount(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password,
        access_key=generate_random_key(),
    )

    try:
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    except IntegrityError:
        raise raise_400_bad_request(message=f"The username {payload.username} is already registered.")


def authenticate_user(username: str, password: str) -> UserAccount:
    engine = create_engine(settings.RDS_URI, echo=True)
    with Session(engine) as session:
        user = session.exec(select(UserAccount).where(UserAccount.username == username)).first()

        if not user:
            raise raise_404_not_found(message=f"The username {username} is not registered.")

        if not user.is_active:
            raise raise_403_forbidden(message=f"The account for username {username} is not activated.")

        if not pwd_context.verify_password(password, user.hashed_password):
            raise raise_401_unauthorized(message="Incorrect password.")

        return user


def activate_user_account(user_id: int) -> UserAccount:
    engine = create_engine(settings.RDS_URI, echo=True)

    with Session(engine) as session:
        user = session.get(UserAccount, user_id)
        user.is_active = True
        session.add(user)
        session.commit()
        session.refresh(user)

    return user


def read_user_by_username(username: str) -> UserAccount:
    engine = create_engine(settings.RDS_URI, echo=True)

    with Session(engine) as session:
        user = session.exec(select(UserAccount).where(UserAccount.username == username)).first()

    if not user:
        raise raise_404_not_found(message=f"The username {username} is not registered.")

    return user

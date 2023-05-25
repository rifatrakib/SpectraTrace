from passlib.context import CryptContext


class PasswordContext:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_plain_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(password, hashed_password)


def get_password_context() -> PasswordContext:
    return PasswordContext()


pwd_context: PasswordContext = get_password_context()

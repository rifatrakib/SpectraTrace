from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(
        title="username",
        decription="""
            Unique username containing letters, numbers, and
            any of (., _, -, @) in between 5 to 32 characters.
        """,
        regex=r"^[\w.@_-]{5,32}$",
        min_length=5,
        max_length=32,
        example="admin",
    )
    email: EmailStr = Field(
        title="email",
        decription="Unique email that can be used for user account activation.",
        example="admin@spectratrace.io",
    )

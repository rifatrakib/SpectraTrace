from datetime import datetime

from pydantic import Field

from server.schemas.base import BaseResponseSchema
from server.schemas.common.users import UserBase


class UserResponseSchema(BaseResponseSchema, UserBase):
    id: int = Field(title="User ID", description="User ID", example=1)
    created_at: datetime = Field(
        title="User creation date",
        description="User creation date",
        example="2021-01-01T00:00:00.000000",
    )
    last_updated_at: datetime = Field(
        title="User update date",
        description="User update date",
        example="2021-01-01T00:00:00.000000",
    )


class UserAccessKeyResponseSchema(BaseResponseSchema):
    access_key: str = Field(title="User access key", description="User access key", example="1234567890")

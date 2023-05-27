from pydantic import Field

from server.schemas.base import BaseResponseSchema
from server.schemas.common.users import UserBase


class UserResponseSchema(BaseResponseSchema, UserBase):
    id: int = Field(title="User ID", description="User ID", example=1)


class UserAccessKeyResponseSchema(BaseResponseSchema):
    access_key: str = Field(title="User access key", description="User access key", example="1234567890")

from pydantic import Field

from server.schemas.base import BaseResponseSchema
from server.schemas.common.users import UserBase


class UserResponseSchema(BaseResponseSchema, UserBase):
    id: int = Field(title="User ID", description="User ID", example=1)

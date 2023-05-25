from typing import Any, List, Union

from pydantic import BaseModel, Extra

from server.utils.formatters import format_dict_key_to_camel_case


class BaseAPISchema(BaseModel):
    class Config:
        orm_mode: bool = True
        allow_population_by_field_name: bool = True
        alias_generator: Any = format_dict_key_to_camel_case


class BaseRequestSchema(BaseAPISchema):
    class Config:
        extra = Extra.forbid


class BaseResponseSchema(BaseAPISchema):
    pass


class HealthResponseSchema(BaseResponseSchema):
    APP_NAME: str
    MODE: str
    DEBUG: bool


class MessageResponseSchema(BaseResponseSchema):
    loc: Union[List[str], None] = None
    msg: str
    type: Union[str, None] = None

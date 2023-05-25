from datetime import datetime
from typing import Union

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

from server.utils.formatters import format_datetime_into_isoformat


class BaseModelConfig(BaseModel):
    class Config:
        use_enum_values = True
        validate_assignment = True
        allow_population_by_field_name: bool = True
        json_encoders: dict = {datetime: format_datetime_into_isoformat}


class BaseSQLTable(SQLModel, BaseModelConfig):
    id: int = Field(index=True, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: Union[datetime, None] = Field(default=None)

    def update(self):
        self.last_updated_at = datetime.utcnow()
        return super().update()

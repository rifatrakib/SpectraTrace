from typing import Union

from pydantic import BaseSettings, Extra, Field


class RootConfig(BaseSettings):
    class Config:
        env_file_encoding = "UTF-8"
        env_nested_delimiter = "__"
        extra = Extra.forbid


class BaseConfig(RootConfig):
    APP_NAME: str

    # SQL Database Configurations
    POSTGRES_HOST: Union[str, None] = Field(default=None)
    POSTGRES_PORT: Union[str, None] = Field(default=None)
    POSTGRES_USER: Union[str, None] = Field(default=None)
    POSTGRES_PASSWORD: Union[str, None] = Field(default=None)
    POSTGRES_DB: Union[str, None] = Field(default=None)

    # Cache Servers Configurations
    REDIS_HOST: str
    REDIS_PORT: int

    # JWT Configurations
    JWT_SECRET_KEY: str
    JWT_SUBJECT: str
    JWT_ALGORITHM: str
    JWT_MIN: int
    JWT_HOUR: int
    JWT_DAY: int

    class Config:
        env_file = "configurations/.env"

    @property
    def RDS_URI(self) -> str:
        username = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        db_name = self.POSTGRES_DB

        if not all([username, password, host, port, db_name]):
            return "sqlite:///database.db"
        return f"postgresql://{username}:{password}@{host}:{port}/{db_name}"

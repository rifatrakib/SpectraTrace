from functools import lru_cache
from typing import Type

from decouple import config
from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    # RabbitMQ Configurations
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

    class Config:
        env_file = "configurations/.env"

    @property
    def RABBITMQ_URI(self) -> str:
        username = self.RABBITMQ_DEFAULT_USER
        password = self.RABBITMQ_DEFAULT_PASS
        host = self.RABBITMQ_HOST
        port = self.RABBITMQ_PORT
        return f"amqp://{username}:{password}@{host}:{port}"


class DevelopmentConfig(BaseConfig):
    class Config:
        env_file = "configurations/.env.development"


class StagingConfig(BaseConfig):
    class Config:
        env_file = "configurations/.env.staging"


class ProductionConfig(BaseConfig):
    class Config:
        env_file = "configurations/.env.production"


@lru_cache()
def get_settings() -> Type[BaseConfig]:
    mode = config("MODE", default="development", cast=str)

    if mode == "staging":
        return StagingConfig()
    elif mode == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()


settings: Type[BaseConfig] = get_settings()

from functools import lru_cache
from typing import Type

from decouple import config
from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    # Message Broker Configurations
    BROKER_HOST: str
    BROKER_PORT: int

    class Config:
        env_file = "configurations/.env"

    @property
    def BROKER_URI(self) -> str:
        host = self.BROKER_HOST
        port = self.BROKER_PORT
        return f"redis://{host}:{port}"


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

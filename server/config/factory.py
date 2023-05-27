from functools import lru_cache
from typing import Type

from decouple import config

from server.config.environments.base import BaseConfig
from server.config.environments.development import DevelopmentConfig
from server.config.environments.production import ProductionConfig
from server.config.environments.staging import StagingConfig


class SettingsFactory:
    def __init__(self, mode: str):
        self.mode = mode

    def __call__(self) -> Type[BaseConfig]:
        if self.mode == "staging":
            return StagingConfig()
        elif self.mode == "production":
            return ProductionConfig()
        else:
            return DevelopmentConfig()


@lru_cache()
def get_settings() -> Type[BaseConfig]:
    factory = SettingsFactory(mode=config("MODE", default="development", cast=str))
    settings = factory()
    return settings


settings: Type[BaseConfig] = get_settings()

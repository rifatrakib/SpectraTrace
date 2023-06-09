from functools import lru_cache
from time import time
from typing import Type

from decouple import config
from pydantic import parse_file_as

from server.config.environments.base import BaseConfig
from server.config.environments.development import DevelopmentConfig
from server.config.environments.production import ProductionConfig
from server.config.environments.staging import StagingConfig
from server.schemas.common.audit import MetadataSchema
from server.schemas.inc.audit import AuditRequestSchema


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
    start_time = time()
    settings = factory()
    execution_time = (time() - start_time) * 1000

    event_data: AuditRequestSchema = parse_file_as(
        type_=AuditRequestSchema,
        path="server/templates/events/env-events.json",
    )

    event_data.event.total_duration = execution_time
    event_data.event.latency = execution_time / 3 * 2
    event_data.resource.detail["store"] = f"configurations/.env.{settings.MODE}"
    event_data.metadata = [
        MetadataSchema(
            is_metric=False,
            name="configurations",
            value=settings.json(),
        ),
    ]

    with open("config-event.json", "w") as writer:
        writer.write(event_data.json())

    return settings


settings: Type[BaseConfig] = get_settings()

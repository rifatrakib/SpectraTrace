from server.config.environments.base import BaseConfig


class StagingConfig(BaseConfig):
    DEBUG: bool = True
    MODE: str = "staging"

    class Config:
        env_file = "configurations/.env.staging"

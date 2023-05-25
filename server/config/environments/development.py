from server.config.environments.base import BaseConfig


class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    MODE: str = "development"

    class Config:
        env_file = "configurations/.env.development"

from server.config.environments.base import BaseConfig


class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    MODE: str = "production"

    class Config:
        env_file = "configurations/.env.production"

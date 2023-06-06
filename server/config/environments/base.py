from pydantic import BaseSettings, Extra


class RootConfig(BaseSettings):
    class Config:
        env_file_encoding = "UTF-8"
        env_nested_delimiter = "__"
        extra = Extra.forbid


class BaseConfig(RootConfig):
    APP_NAME: str

    # SQL Database Configurations
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

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

    # InfluxDB Configurations
    INFLUXDB_HOST: str
    INFLUXDB_PORT: int
    INFLUXDB_USER: str
    INFLUXDB_PASSWORD: str
    INFLUXDB_ORG: str

    # Message Broker Configurations
    BROKER_HOST: str
    BROKER_PORT: int

    class Config:
        env_file = "configurations/.env"

    @property
    def RDS_URI(self) -> str:
        username = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        db_name = self.POSTGRES_DB
        return f"postgresql://{username}:{password}@{host}:{port}/{db_name}"

    @property
    def RDS_URI_ASYNC(self) -> str:
        uri = self.RDS_URI
        return uri.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def BROKER_URI(self) -> str:
        host = self.BROKER_HOST
        port = self.BROKER_PORT
        return f"redis://{host}:{port}"

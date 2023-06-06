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

    # RabbitMQ Configurations
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

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
    def RABBITMQ_URI(self) -> str:
        username = self.RABBITMQ_DEFAULT_USER
        password = self.RABBITMQ_DEFAULT_PASS
        host = self.RABBITMQ_HOST
        port = self.RABBITMQ_PORT
        return f"amqp://{username}:{password}@{host}:{port}"

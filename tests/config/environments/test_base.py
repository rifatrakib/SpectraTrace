import pytest

from server.config.environments.base import BaseConfig, RootConfig


class TestRootConfig:
    def test_extra_fields(self):
        """Tests that an error is raised if any extra fields are present."""
        with pytest.raises(ValueError):
            RootConfig(
                database_url="postgres://user:password@localhost:5432/mydb",  # pragma: allowlist secret
                extra_field="extra",
            )

    def test_env_file_encoding(self):
        """Tests that the env_file_encoding attribute is correctly set."""
        assert RootConfig.Config.env_file_encoding == "UTF-8"

    def test_env_nested_delimiter(self):
        """Tests that the env_nested_delimiter attribute is correctly set."""
        assert RootConfig.Config.env_nested_delimiter == "__"


class TestBaseConfig:
    def test_rds_uri_returns_correct_uri(self):
        """Tests that the RDS_URI property returns a URI with the correct
        format when all required variables are present."""
        config = BaseConfig(
            APP_NAME="test_app",
            POSTGRES_HOST="localhost",
            POSTGRES_PORT="5432",
            POSTGRES_USER="test_user",
            POSTGRES_PASSWORD="test_password",  # pragma: allowlist secret
            POSTGRES_DB="test_db",
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            JWT_SECRET_KEY="test_secret",  # pragma: allowlist secret
            JWT_SUBJECT="test_subject",
            JWT_ALGORITHM="HS256",
            JWT_MIN=30,
            JWT_HOUR=1,
            JWT_DAY=1,
        )
        assert (
            config.RDS_URI == "postgresql://test_user:test_password@localhost:5432/test_db"  # pragma: allowlist secret
        )

    def test_config_loads_env_vars(self):
        configs = {}
        with open("configurations/.env", "r") as reader:
            for line in reader.readlines():
                if line.startswith("#") or not line.strip():
                    continue

                key, value = line.strip().split("=")
                configs[key] = value

        """Tests that the Config class correctly loads environment variables from the specified file."""
        config = BaseConfig()
        assert config.POSTGRES_HOST == configs["POSTGRES_HOST"]
        assert config.POSTGRES_PORT == configs["POSTGRES_PORT"]
        assert config.POSTGRES_USER == configs["POSTGRES_USER"]
        assert config.POSTGRES_PASSWORD == configs["POSTGRES_PASSWORD"]
        assert config.POSTGRES_DB == configs["POSTGRES_DB"]
        assert config.REDIS_HOST == configs["REDIS_HOST"]
        assert config.REDIS_PORT == int(configs["REDIS_PORT"])
        assert config.JWT_SECRET_KEY == configs["JWT_SECRET_KEY"]
        assert config.JWT_SUBJECT == configs["JWT_SUBJECT"]
        assert config.JWT_ALGORITHM == configs["JWT_ALGORITHM"]
        assert config.JWT_MIN == int(configs["JWT_MIN"])
        assert config.JWT_HOUR == int(configs["JWT_HOUR"])
        assert config.JWT_DAY == int(configs["JWT_DAY"])

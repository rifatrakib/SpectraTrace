import pytest

from server.config.environments.production import ProductionConfig


class TestProductionConfig:
    def test_setting_required_configurations(self):
        """Tests setting all required configurations and properties."""
        config = ProductionConfig(
            APP_NAME="test_app",
            POSTGRES_HOST="localhost",
            POSTGRES_PORT="5432",
            POSTGRES_USER="test_user",
            POSTGRES_PASSWORD="test_password",  # pragma: allowlist secret
            POSTGRES_DB="test_db",
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            JWT_SECRET_KEY="test_secret_key",  # pragma: allowlist secret
            JWT_SUBJECT="test_subject",
            JWT_ALGORITHM="HS256",
            JWT_MIN=30,
            JWT_HOUR=1,
            JWT_DAY=1,
        )

        assert config.APP_NAME == "test_app"
        assert config.POSTGRES_HOST == "localhost"
        assert config.POSTGRES_PORT == "5432"
        assert config.POSTGRES_USER == "test_user"
        assert config.POSTGRES_PASSWORD == "test_password"  # pragma: allowlist secret
        assert config.POSTGRES_DB == "test_db"
        assert config.REDIS_HOST == "localhost"
        assert config.REDIS_PORT == 6379
        assert config.JWT_SECRET_KEY == "test_secret_key"  # pragma: allowlist secret
        assert config.JWT_SUBJECT == "test_subject"
        assert config.JWT_ALGORITHM == "HS256"
        assert config.JWT_MIN == 30
        assert config.JWT_HOUR == 1
        assert config.JWT_DAY == 1
        assert (
            config.RDS_URI == "postgresql://test_user:test_password@localhost:5432/test_db"  # pragma: allowlist secret
        )
        assert config.DEBUG is False
        assert config.MODE == "production"

    def test_setting_optional_configurations_to_none(self):
        """Tests setting optional configurations to None."""
        config = ProductionConfig(
            APP_NAME="test_app",
            POSTGRES_HOST=None,
            POSTGRES_PORT=None,
            POSTGRES_USER=None,
            POSTGRES_PASSWORD=None,
            POSTGRES_DB=None,
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            JWT_SECRET_KEY="test_secret_key",  # pragma: allowlist secret
            JWT_SUBJECT="test_subject",
            JWT_ALGORITHM="HS256",
            JWT_MIN=30,
            JWT_HOUR=1,
            JWT_DAY=1,
        )

        assert config.POSTGRES_HOST is None
        assert config.POSTGRES_PORT is None
        assert config.POSTGRES_USER is None
        assert config.POSTGRES_PASSWORD is None
        assert config.POSTGRES_DB is None
        assert config.RDS_URI == "sqlite:///database.db"

    def test_loading_environment_variables_from_env_file(self, monkeypatch):
        """Tests loading environment variables from `configurations/.env`
        file."""
        monkeypatch.setenv("APP_NAME", "test_app")
        monkeypatch.setenv("POSTGRES_HOST", "localhost")
        monkeypatch.setenv("POSTGRES_PORT", "5432")
        monkeypatch.setenv("POSTGRES_USER", "test_user")
        monkeypatch.setenv("POSTGRES_PASSWORD", "test_password")  # pragma: allowlist secret
        monkeypatch.setenv("POSTGRES_DB", "test_db")
        monkeypatch.setenv("REDIS_HOST", "localhost")
        monkeypatch.setenv("REDIS_PORT", "6379")
        monkeypatch.setenv("JWT_SECRET_KEY", "test_secret_key")  # pragma: allowlist secret
        monkeypatch.setenv("JWT_SUBJECT", "test_subject")
        monkeypatch.setenv("JWT_ALGORITHM", "HS256")
        monkeypatch.setenv("JWT_MIN", "30")
        monkeypatch.setenv("JWT_HOUR", "1")
        monkeypatch.setenv("JWT_DAY", "1")

        config = ProductionConfig()
        assert config.APP_NAME == "test_app"
        assert config.POSTGRES_HOST == "localhost"
        assert config.POSTGRES_PORT == "5432"
        assert config.POSTGRES_USER == "test_user"
        assert config.POSTGRES_PASSWORD == "test_password"  # pragma: allowlist secret
        assert config.POSTGRES_DB == "test_db"
        assert config.REDIS_HOST == "localhost"
        assert config.REDIS_PORT == 6379
        assert config.JWT_SECRET_KEY == "test_secret_key"  # pragma: allowlist secret
        assert config.JWT_SUBJECT == "test_subject"
        assert config.JWT_ALGORITHM == "HS256"
        assert config.JWT_MIN == 30
        assert config.JWT_HOUR == 1
        assert config.JWT_DAY == 1
        assert (
            config.RDS_URI == "postgresql://test_user:test_password@localhost:5432/test_db"  # pragma: allowlist secret
        )
        assert config.DEBUG is False
        assert config.MODE == "production"

    # Tests setting invalid values for configurations.
    def test_setting_invalid_values_for_configurations(self):
        with pytest.raises(ValueError):
            ProductionConfig(
                APP_NAME="test_app",
                POSTGRES_HOST="localhost",
                POSTGRES_PORT="5432",
                POSTGRES_USER="test_user",
                POSTGRES_PASSWORD="test_password",  # pragma: allowlist secret
                POSTGRES_DB="test_db",
                REDIS_HOST="localhost",
                REDIS_PORT="invalid_port",
                JWT_SECRET_KEY="test_secret_key",  # pragma: allowlist secret
                JWT_SUBJECT="test_subject",
                JWT_ALGORITHM="HS256",
                JWT_MIN=30,
                JWT_HOUR=1,
                JWT_DAY=1,
            )

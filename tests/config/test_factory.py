from server.config.environments.base import BaseConfig
from server.config.environments.development import DevelopmentConfig
from server.config.environments.production import ProductionConfig
from server.config.environments.staging import StagingConfig
from server.config.factory import SettingsFactory, get_settings


class TestSettingsFactory:
    def test_mode_staging_returns_StagingConfig(self):
        """Tests that the factory returns an instance of StagingConfig when
        mode is "staging"."""
        factory = SettingsFactory(mode="staging")
        config = factory()
        assert isinstance(config, StagingConfig)

    def test_mode_production_returns_ProductionConfig(self):
        """Tests that the factory returns an instance of ProductionConfig when
        mode is "production"."""
        factory = SettingsFactory(mode="production")
        config = factory()
        assert isinstance(config, ProductionConfig)

    def test_None_returns_DevelopmentConfig(self):
        """Tests that the factory returns an instance of DevelopmentConfig when
        mode is None."""
        factory = SettingsFactory(mode=None)
        config = factory()
        assert isinstance(config, DevelopmentConfig)

    def test_call_returns_instance_of_BaseConfig(self):
        """Tests that the factory returns an instance of a subclass of
        BaseConfig."""
        factory = SettingsFactory(mode="development")
        config = factory()
        assert isinstance(config, BaseConfig)

    def test_mode_any_other_string_returns_DevelopmentConfig(self):
        """Tests that the factory returns an instance of DevelopmentConfig when
        mode is any other string."""
        factory = SettingsFactory(mode="test")
        config = factory()
        assert isinstance(config, DevelopmentConfig)

    def test_call_returns_different_instances_for_different_modes(self):
        """Tests that the factory returns different instances of BaseConfig
        subclasses for different modes."""
        factory1 = SettingsFactory(mode="development")
        config1 = factory1()
        factory2 = SettingsFactory(mode="staging")
        config2 = factory2()
        assert type(config1) != type(config2)


class TestGetSettings:
    def test_get_settings_returns_valid_instance(self):
        """Tests that the function returns a valid instance of BaseConfig."""
        settings = get_settings()
        assert isinstance(settings, BaseConfig)

    def test_get_settings_mode_not_set(self, monkeypatch):
        """Tests that the function returns an instance of DevelopmentConfig
        when MODE environment variable is not set."""
        monkeypatch.delenv("MODE", raising=False)
        settings = get_settings()
        assert isinstance(settings, DevelopmentConfig)

    def test_get_settings_invalid_mode(self, monkeypatch):
        """Tests that the function returns an instance of DevelopmentConfig
        when MODE environment variable is set to an invalid value."""
        monkeypatch.setenv("MODE", "invalid_mode")
        settings = get_settings()
        assert isinstance(settings, DevelopmentConfig)

    def test_get_settings_returns_same_instance(self):
        """Tests that the function returns the same instance of BaseConfig when
        called multiple times."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_get_settings_invalid_configurations(self, monkeypatch):
        """Tests that the function handles invalid values for POSTGRES_HOST,
        POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB,
        JWT_SECRET_KEY, JWT_SUBJECT, JWT_ALGORITHM, JWT_MIN, JWT_HOUR, JWT_DAY,
        REDIS_HOST, REDIS_PORT."""
        monkeypatch.setenv("POSTGRES_HOST", "invalid_host")
        monkeypatch.setenv("POSTGRES_PORT", "invalid_port")
        monkeypatch.setenv("POSTGRES_USER", "invalid_user")
        monkeypatch.setenv("POSTGRES_PASSWORD", "invalid_password")
        monkeypatch.setenv("POSTGRES_DB", "invalid_db")
        monkeypatch.setenv("JWT_SECRET_KEY", "")
        monkeypatch.setenv("JWT_SUBJECT", "")
        monkeypatch.setenv("JWT_ALGORITHM", "")
        monkeypatch.setenv("JWT_MIN", "invalid_min")
        monkeypatch.setenv("JWT_HOUR", "invalid_hour")
        monkeypatch.setenv("JWT_DAY", "invalid_day")
        monkeypatch.setenv("REDIS_HOST", "")
        monkeypatch.setenv("REDIS_PORT", "invalid_port")
        settings = get_settings()
        assert isinstance(settings, BaseConfig)

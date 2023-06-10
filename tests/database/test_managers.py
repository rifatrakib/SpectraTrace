import json
from unittest.mock import Mock, patch

import pytest
from redis import Redis

from server.config.factory import settings
from server.database.cache.ops import activate_from_cache, cache_data, is_in_cache
from server.database.managers import create_db_and_tables, get_redis_client, ping_redis_server


class TestCreateDbAndTables:
    @patch("server.database.managers.create_engine")
    @patch("server.database.managers.UserTables.metadata.create_all")
    def test_create_db_and_tables_success(self, mock_create_all, mock_create_engine):
        """Mock the create_engine function and its return value."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        create_db_and_tables()
        mock_create_engine.assert_called_once_with(settings.RDS_URI, echo=True)
        mock_create_all.assert_called_once_with(mock_engine)

    @patch("server.database.managers.create_engine", side_effect=Exception("Invalid URI"))
    def test_create_db_and_tables_invalid_uri(self, mock_create_engine):
        """Call the function under test and assert that it raises an
        exception."""
        with pytest.raises(Exception, match="Invalid URI"):
            create_db_and_tables()

    @patch("server.database.managers.create_engine")
    @patch("server.database.managers.UserTables.metadata.create_all", side_effect=Exception("Metadata already exists"))
    def test_create_db_and_tables_metadata_exists(self, mock_create_all, mock_create_engine):
        """Mock the create_engine function and its return value."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        # Call the function under test and assert that it raises an exception
        with pytest.raises(Exception, match="Metadata already exists"):
            create_db_and_tables()

        mock_create_engine.assert_called_once_with(settings.RDS_URI, echo=True)
        mock_create_all.assert_called_once_with(mock_engine)


class TestRedisFunctions:
    def test_get_redis_client(self, monkeypatch):
        """Patch the Redis function parameters."""
        monkeypatch.setattr(settings, "REDIS_HOST", "localhost")
        monkeypatch.setattr(settings, "REDIS_PORT", 6379)
        redis_client = get_redis_client()
        assert redis_client.connection_pool.connection_kwargs["host"] == "localhost"
        assert redis_client.connection_pool.connection_kwargs["port"] == 6379

    @patch("server.database.managers.get_redis_client")
    def test_ping_redis_server(self, mock_get_redis_client):
        """Mock the get_redis_client function and its return value."""
        mock_client = Mock(spec=Redis)
        mock_get_redis_client.return_value = mock_client
        mock_client.ping.return_value = True

        # Call the function under test
        result = ping_redis_server()
        mock_get_redis_client.assert_called_once()
        mock_client.ping.assert_called_once()
        assert result is True

    @patch("server.database.managers.get_redis_client")
    def test_cache_data(self, mock_get_redis_client):
        # Mock the Redis client
        mock_client = Mock(spec=Redis)
        mock_get_redis_client.return_value = mock_client

        # Call the function under test
        cache_data(key="test_key", data="test_data", ttl=3600)
        mock_get_redis_client.assert_called_once()
        mock_client.set.assert_called_once_with("test_key", "test_data", ex=3600)

    @patch("server.database.managers.get_redis_client")
    def test_is_in_cache_key_exists(self, mock_get_redis_client):
        # Mock the Redis client
        mock_client = Mock(spec=Redis)
        mock_get_redis_client.return_value = mock_client
        mock_client.exists.return_value = True

        # Call the function under test
        result, _ = is_in_cache(key="test_key")
        mock_get_redis_client.assert_called_once()
        mock_client.exists.assert_called_once_with("test_key")
        assert result is True

    @patch("server.database.managers.get_redis_client")
    def test_is_in_cache_key_does_not_exist(self, mock_get_redis_client):
        # Mock the Redis client
        mock_client = Mock(spec=Redis)
        mock_get_redis_client.return_value = mock_client
        mock_client.exists.return_value = False

        # Call the function under test
        result, _ = is_in_cache(key="test_key")
        mock_get_redis_client.assert_called_once()
        mock_client.exists.assert_called_once_with("test_key")
        assert result is None

    @patch("server.database.managers.get_redis_client", side_effect=Exception("Token expired or invalid."))
    def test_is_in_cache_exception(self, mock_get_redis_client):
        # Mock the Redis client
        mock_client = Mock(spec=Redis)
        mock_get_redis_client.return_value = mock_client

        with pytest.raises(Exception):
            is_in_cache(key="test_key")

        mock_get_redis_client.assert_called_once()

    @patch("server.database.managers.get_redis_client")
    def test_activate_from_cache_success(self, mock_get_redis_client):
        # Mock the Redis client
        mock_client = Mock(spec=Redis)
        mock_get_redis_client.return_value = mock_client

        # Mock the Redis client's get method to return JSON data
        mock_data = {"key": "value"}
        mock_client.get.return_value = json.dumps(mock_data).encode("utf-8")

        # Call the function under test
        result, _ = activate_from_cache(key="test_key")

        # Assertions
        mock_get_redis_client.assert_called_once()
        mock_client.get.assert_called_once_with("test_key")
        mock_client.delete.assert_called_once_with("test_key")
        assert result == mock_data

    @patch("server.database.managers.get_redis_client", side_effect=Exception("Token expired or invalid."))
    def test_activate_from_cache_exception(self, mock_get_redis_client):
        # Mock the Redis client
        mock_client = Mock(spec=Redis)
        mock_get_redis_client.return_value = mock_client

        with pytest.raises(Exception):
            activate_from_cache(key="test_key")

        mock_get_redis_client.assert_called_once()

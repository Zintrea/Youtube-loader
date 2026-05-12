import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from config_settings.AppConfig import AppConfig


class TestAppConfig:
    def test_instantiation(self, app_config):
        assert app_config is not None
        assert isinstance(app_config, AppConfig)

    def test_default_values(self, app_config):
        assert app_config.download_dir == "Downloads"
        assert app_config.server_host == "0.0.0.0"
        assert app_config.server_port == 8000
        assert app_config.allowed_extensions == ["mp4", "mp3", "wav", "webm"]

    def test_custom_download_dir(self):
        config = AppConfig(download_dir="/custom/path")
        assert config.download_dir == "/custom/path"
        assert config.server_host == "0.0.0.0"
        assert config.server_port == 8000

    def test_custom_server_host(self):
        config = AppConfig(server_host="127.0.0.1")
        assert config.server_host == "127.0.0.1"
        assert config.download_dir == "Downloads"

    def test_custom_server_port(self):
        config = AppConfig(server_port=3000)
        assert config.server_port == 3000

    def test_custom_allowed_extensions(self):
        config = AppConfig(allowed_extensions=["mkv", "flac"])
        assert config.allowed_extensions == ["mkv", "flac"]

    def test_multiple_custom_values(self):
        config = AppConfig(
            download_dir="/tmp",
            server_host="localhost",
            server_port=9000,
            allowed_extensions=["avi"],
        )
        assert config.download_dir == "/tmp"
        assert config.server_host == "localhost"
        assert config.server_port == 9000
        assert config.allowed_extensions == ["avi"]

    def test_independent_instances_have_independent_extensions(self):
        """Ensure allowed_extensions uses default_factory (not shared list)."""
        c1 = AppConfig()
        c2 = AppConfig()
        c1.allowed_extensions.append("custom")
        assert "custom" not in c2.allowed_extensions

    def test_attributes_are_correct_types(self, app_config):
        assert isinstance(app_config.download_dir, str)
        assert isinstance(app_config.server_host, str)
        assert isinstance(app_config.server_port, int)
        assert isinstance(app_config.allowed_extensions, list)

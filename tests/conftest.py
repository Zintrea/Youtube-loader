import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from config_settings.AppConfig import AppConfig
from Main import app


@pytest.fixture
def app_config():
    return AppConfig()

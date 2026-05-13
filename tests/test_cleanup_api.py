"""Tests for the new POST /api/cleanup endpoint.

Uses FastAPI's TestClient with a dependency override to isolate the download directory
to a temporary path per test.
"""

import os
import time

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from fastapi.testclient import TestClient
from Main import app
from api_routes.FileRouter import get_app_config


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def override_download_dir(tmp_path):
    """Override the download directory to a temporary path for every test."""
    def override_config():
        cfg = MagicMock()
        cfg.download_dir = str(tmp_path)
        cfg.cleanup_max_age = 60
        return cfg

    app.dependency_overrides[get_app_config] = override_config
    yield
    app.dependency_overrides.clear()


class TestCleanup:
    """Tests for POST /api/cleanup."""

    def test_cleanup_deletes_old_files(self, client, tmp_path):
        """Files older than the configured age should be deleted."""
        (tmp_path / "old.mp4").write_text("old")
        old_mtime = time.time() - (2 * 3600)
        os.utime(tmp_path / "old.mp4", (old_mtime, old_mtime))

        (tmp_path / "new.mp4").write_text("new")

        response = client.post("/api/cleanup")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 1
        assert data["total_files_before"] == 2
        assert data["total_files_after"] == 1

        assert not (tmp_path / "old.mp4").exists()
        assert (tmp_path / "new.mp4").exists()

    def test_cleanup_no_old_files(self, client, tmp_path):
        """When no files are old, nothing is deleted."""
        (tmp_path / "recent.mp4").write_text("data")

        response = client.post("/api/cleanup")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 0

    def test_cleanup_empty_directory(self, client):
        """Cleanup on empty directory returns 0 deleted."""
        response = client.post("/api/cleanup")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 0
        assert data["total_files_before"] == 0

    def test_cleanup_uses_config_max_age(self, client, tmp_path):
        """Respect the cleanup_max_age from AppConfig."""
        medium = tmp_path / "medium.mp4"
        medium.write_text("data")
        # 30 min old
        medium_mtime = time.time() - (30 * 60)
        os.utime(medium, (medium_mtime, medium_mtime))

        # With default 60 min config -> keep
        assert medium.exists()
        response = client.post("/api/cleanup")
        assert response.json()["deleted_count"] == 0

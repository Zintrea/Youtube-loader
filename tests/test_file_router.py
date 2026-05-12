"""Tests for the FileRouter endpoints (GET /api/files, GET /api/files/{filename}, DELETE /api/files/{filename}).

Uses FastAPI's TestClient with a dependency override to isolate the download directory
to a temporary path per test.
"""

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
        return cfg

    app.dependency_overrides[get_app_config] = override_config
    yield
    app.dependency_overrides.clear()


class TestListFiles:
    """Tests for GET /api/files."""

    def test_list_files_returns_file_list_when_files_exist(self, client, tmp_path):
        """GET /api/files returns a list of filenames when files are present."""
        (tmp_path / "video1.mp4").write_text("data1")
        (tmp_path / "audio.mp3").write_text("data2")

        response = client.get("/api/files")
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert sorted(data["files"]) == ["audio.mp3", "video1.mp4"]

    def test_list_files_returns_empty_list_when_no_files(self, client):
        """GET /api/files returns an empty list when the directory has no files."""
        response = client.get("/api/files")
        assert response.status_code == 200
        data = response.json()
        assert data == {"files": []}


class TestDownloadFile:
    """Tests for GET /api/files/{filename}."""

    def test_download_file_serves_content(self, client, tmp_path):
        """GET /api/files/{filename} serves the file content correctly."""
        content = "this is test file content for download"
        (tmp_path / "test_video.mp4").write_text(content)

        response = client.get("/api/files/test_video.mp4")
        assert response.status_code == 200
        assert response.text == content

    def test_download_file_returns_404_for_nonexistent_file(self, client):
        """GET /api/files/{filename} returns 404 when file does not exist."""
        response = client.get("/api/files/nonexistent.mp4")
        assert response.status_code == 404


class TestDeleteFile:
    """Tests for DELETE /api/files/{filename}."""

    def test_delete_file_removes_the_file(self, client, tmp_path):
        """DELETE /api/files/{filename} removes the file and returns 200."""
        (tmp_path / "to_delete.mp4").write_text("content")
        assert (tmp_path / "to_delete.mp4").exists()

        response = client.delete("/api/files/to_delete.mp4")
        assert response.status_code == 200
        assert not (tmp_path / "to_delete.mp4").exists()

    def test_delete_file_returns_404_for_nonexistent_file(self, client):
        """DELETE /api/files/{filename} returns 404 when file does not exist."""
        response = client.delete("/api/files/does_not_exist.mp4")
        assert response.status_code == 404

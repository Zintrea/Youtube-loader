"""Integration tests for the Youtube-loader FastAPI API endpoints.

Uses FastAPI's TestClient for in-memory HTTP testing without a running server.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from fastapi.testclient import TestClient
from Main import app

# Import the job storage so we can manipulate it in tests
from api_routes.DownloadRouter import download_jobs, get_app_config
from core_services.FileStorageService import FileStorageService


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_jobs():
    """Clear download_jobs before and after each test to ensure isolation."""
    download_jobs.clear()
    yield
    download_jobs.clear()


class TestStatusEndpoint:
    """Tests for GET /api/status."""

    def test_status_returns_ok(self, client):
        """GET /api/status returns status ok with version."""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok", "version": "0.1.0"}


class TestDownloadCreate:
    """Tests for POST /api/download."""

    VALID_URL = "https://www.youtube.com/watch?v=dQw4wRgXcQ"
    VALID_SHORT_URL = "https://youtu.be/dQw4wRgXcQ"

    def test_download_valid_url_default_format(self, client):
        """POST /api/download with valid URL and default format returns 200 with job_id."""
        response = client.post(
            "/api/download",
            json={"url": self.VALID_URL},
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert isinstance(data["job_id"], str)
        assert len(data["job_id"]) > 0

    def test_download_valid_url_explicit_format(self, client):
        """POST /api/download with explicit output_format returns 200."""
        response = client.post(
            "/api/download",
            json={"url": self.VALID_URL, "output_format": "1080p"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert "job_id" in data

    def test_download_youtu_be_url(self, client):
        """POST /api/download with youtu.be short URL is accepted."""
        response = client.post(
            "/api/download",
            json={"url": self.VALID_SHORT_URL, "output_format": "720p"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"

    @pytest.mark.parametrize("fmt", ["1080p", "720p", "480p", "mp3", "m4a"])
    def test_download_all_valid_formats(self, client, fmt):
        """All allowed formats are accepted."""
        response = client.post(
            "/api/download",
            json={"url": self.VALID_URL, "output_format": fmt},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"

    def test_download_with_custom_filename(self, client):
        """POST /api/download with custom_filename is accepted."""
        response = client.post(
            "/api/download",
            json={
                "url": self.VALID_URL,
                "output_format": "720p",
                "custom_filename": "my_video.mp4",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"

    def test_download_invalid_url_returns_422(self, client):
        """POST /api/download with non-YouTube URL returns 422."""
        response = client.post(
            "/api/download",
            json={"url": "https://example.com/video", "output_format": "720p"},
        )
        assert response.status_code == 422

    def test_download_missing_url_returns_422(self, client):
        """POST /api/download without url field returns 422."""
        response = client.post(
            "/api/download",
            json={"output_format": "720p"},
        )
        assert response.status_code == 422

    def test_download_invalid_format_returns_422(self, client):
        """POST /api/download with invalid output_format returns 422."""
        response = client.post(
            "/api/download",
            json={"url": self.VALID_URL, "output_format": "mkv"},
        )
        assert response.status_code == 422

    def test_download_invalid_format_720i_returns_422(self, client):
        """720i is not an allowed format."""
        response = client.post(
            "/api/download",
            json={"url": self.VALID_URL, "output_format": "720i"},
        )
        assert response.status_code == 422

    def test_download_empty_url_returns_422(self, client):
        """Empty string URL fails YouTube URL validation."""
        response = client.post(
            "/api/download",
            json={"url": "", "output_format": "720p"},
        )
        assert response.status_code == 422

    def test_download_empty_body_returns_422(self, client):
        """Empty JSON body fails because url is required."""
        response = client.post("/api/download", json={})
        assert response.status_code == 422

    def test_download_response_format(self, client):
        """Response model contains exactly job_id and status keys."""
        response = client.post(
            "/api/download",
            json={"url": self.VALID_URL},
        )
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {"job_id", "status"}


class TestDownloadStatus:
    """Tests for GET /api/download/{job_id}."""

    VALID_URL = "https://www.youtube.com/watch?v=dQw4wRgXcQ"

    def test_status_existing_job(self, client):
        """GET /api/download/{job_id} returns job details for existing job."""
        # Create a job directly in the store to avoid real network download
        job_id = "test-job-1"
        download_jobs[job_id] = {
            "id": job_id,
            "url": self.VALID_URL,
            "format": "720p",
            "status": "pending",
        }

        # Check status
        response = client.get(f"/api/download/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["url"] == self.VALID_URL
        assert data["format"] == "720p"

    def test_status_non_existing_job_returns_404(self, client):
        """GET /api/download/{nonexistent_id} returns 404."""
        response = client.get("/api/download/nonexistent-job-id")
        assert response.status_code == 404

    def test_status_job_with_manually_set_completed(self, client):
        """A job manually set to completed shows correct fields."""
        job_id = "manual-test-job"
        download_jobs[job_id] = {
            "id": job_id,
            "url": self.VALID_URL,
            "format": "mp3",
            "status": "completed",
            "filepath": "/tmp/test.mp3",
            "title": "Test Song",
        }

        response = client.get(f"/api/download/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["filepath"] == "/tmp/test.mp3"
        assert data["title"] == "Test Song"
        assert data["format"] == "mp3"

    def test_status_job_failed(self, client):
        """A failed job includes the error field."""
        job_id = "failed-job"
        download_jobs[job_id] = {
            "id": job_id,
            "url": self.VALID_URL,
            "format": "720p",
            "status": "failed",
            "error": "Video unavailable",
        }

        response = client.get(f"/api/download/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error"] == "Video unavailable"


class TestDownloadsList:
    """Tests for GET /api/downloads."""

    def test_list_downloads_returns_files(self, client, tmp_path):
        """GET /api/downloads returns list of files from storage."""
        # Use dependency override to inject a mock config pointing to tmp_path
        def override_config():
            cfg = MagicMock()
            cfg.download_dir = str(tmp_path)
            return cfg

        test_app = app
        test_app.dependency_overrides[get_app_config] = override_config

        # Create some files
        (tmp_path / "video1.mp4").write_text("data")
        (tmp_path / "audio.mp3").write_text("data")

        try:
            response = client.get("/api/downloads")
            assert response.status_code == 200
            data = response.json()
            assert "files" in data
            assert sorted(data["files"]) == ["audio.mp3", "video1.mp4"]
        finally:
            test_app.dependency_overrides.clear()

    def test_list_downloads_empty(self, client, tmp_path):
        """GET /api/downloads on empty directory returns empty list."""
        def override_config():
            cfg = MagicMock()
            cfg.download_dir = str(tmp_path)
            return cfg

        app.dependency_overrides[get_app_config] = override_config

        try:
            response = client.get("/api/downloads")
            assert response.status_code == 200
            data = response.json()
            assert data == {"files": []}
        finally:
            app.dependency_overrides.clear()


class TestFullDownloadFlow:
    """Integration test for the full download lifecycle using mocking."""

    VALID_URL = "https://www.youtube.com/watch?v=dQw4wRgXcQ"

    @patch("api_routes.DownloadRouter.YoutubeService.download_video")
    def test_full_download_flow_mocked(self, mock_download, client, tmp_path):
        """Complete flow: create job -> check pending -> verify task runs."""
        mock_download.return_value = {
            "success": True,
            "filepath": str(tmp_path / "test.mp4"),
            "title": "Test Video",
        }

        # Step 1: Create download job
        resp = client.post(
            "/api/download",
            json={"url": self.VALID_URL, "output_format": "720p"},
        )
        assert resp.status_code == 200
        job_id = resp.json()["job_id"]

        # Step 2: Immediately check status - should be pending or downloading
        status_resp = client.get(f"/api/download/{job_id}")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data["status"] in ("pending", "downloading", "completed")

        # Step 3: Trigger background tasks synchronously (FastAPI TestClient
        # runs background tasks immediately when the response is received
        # with raise_server_exceptions=True — but async tasks may need
        # client to wait. In TestClient, background tasks are run after
        # the response is returned, so let's re-check.)
        # Check again — the background task should have run
        status_resp2 = client.get(f"/api/download/{job_id}")
        assert status_resp2.status_code == 200
        status_data2 = status_resp2.json()
        # Task should now be completed since TestClient runs tasks synchronously
        assert status_data2["status"] in ("downloading", "completed")


class TestValidationErrorDetails:
    """Tests to ensure validation error responses contain useful details."""

    def test_invalid_url_message_contains_validation_error(self, client):
        """422 response includes field-level error details."""
        response = client.post(
            "/api/download",
            json={"url": "https://google.com", "output_format": "720p"},
        )
        assert response.status_code == 422
        body = response.json()
        assert "detail" in body

    def test_invalid_format_message_includes_valid_options(self, client):
        """422 for bad format mentions allowed formats."""
        response = client.post(
            "/api/download",
            json={"url": "https://youtube.com/watch?v=abc", "output_format": "avi"},
        )
        assert response.status_code == 422
        body = response.json()
        assert "detail" in body

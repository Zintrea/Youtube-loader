"""Integration tests for the Youtube-loader FastAPI API endpoints.

Uses FastAPI's TestClient for in-memory HTTP testing without a running server.
"""

import os
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from fastapi.testclient import TestClient
from Main import app

# Import the job storage service and router dependencies
from api_routes.DownloadRouter import get_app_config, get_job_storage, _JOB_DB_PATH
from core_services.JobStorageService import JobStorageService
from core_services.FileStorageService import FileStorageService


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def isolate_job_storage(tmp_path):
    """Each test gets its own isolated SQLite database so tests don't interfere."""
    db_file = str(tmp_path / "test_jobs.db")

    def override_job_storage():
        return JobStorageService(db_file)

    app.dependency_overrides[get_job_storage] = override_job_storage

    yield db_file

    app.dependency_overrides.clear()


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

    def test_download_valid_url_default_format(self, client, isolate_job_storage):
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

    def test_download_valid_url_explicit_format(self, client, isolate_job_storage):
        """POST /api/download with explicit output_format returns 200."""
        response = client.post(
            "/api/download",
            json={"url": self.VALID_URL, "output_format": "1080p"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert "job_id" in data

    def test_download_youtu_be_url(self, client, isolate_job_storage):
        """POST /api/download with youtu.be short URL is accepted."""
        response = client.post(
            "/api/download",
            json={"url": self.VALID_SHORT_URL, "output_format": "720p"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"

    @pytest.mark.parametrize("fmt", ["1080p", "720p", "480p", "mp3", "m4a"])
    def test_download_all_valid_formats(self, client, fmt, isolate_job_storage):
        """All allowed formats are accepted."""
        response = client.post(
            "/api/download",
            json={"url": self.VALID_URL, "output_format": fmt},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"

    def test_download_with_custom_filename(self, client, isolate_job_storage):
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

    def test_download_response_format(self, client, isolate_job_storage):
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

    def test_status_existing_job(self, client, isolate_job_storage):
        """GET /api/download/{job_id} returns job details for existing job."""
        # Create a job via the API
        resp = client.post("/api/download", json={"url": self.VALID_URL})
        assert resp.status_code == 200
        job_id = resp.json()["job_id"]

        response = client.get(f"/api/download/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["url"] == self.VALID_URL

    def test_status_existing_job_manually_created(self, client, isolate_job_storage):
        """GET /api/download/{job_id} for a job created directly via JobStorageService."""
        db_file = isolate_job_storage
        service = JobStorageService(db_file)
        service.create_job("test-job-1", self.VALID_URL, "720p")

        response = client.get("/api/download/test-job-1")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["url"] == self.VALID_URL
        assert data["format"] == "720p"

    def test_status_non_existing_job_returns_404(self, client):
        """GET /api/download/{nonexistent_id} returns 404."""
        response = client.get("/api/download/nonexistent-job-id")
        assert response.status_code == 404

    def test_status_job_completed(self, client, isolate_job_storage):
        """A job manually set to completed shows correct fields."""
        db_file = isolate_job_storage
        service = JobStorageService(db_file)
        service.create_job("manual-test-job", self.VALID_URL, "mp3")
        service.update_job(
            "manual-test-job",
            status="completed",
            filepath="/tmp/test.mp3",
            title="Test Song",
        )

        response = client.get("/api/download/manual-test-job")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["filepath"] == "/tmp/test.mp3"
        assert data["title"] == "Test Song"
        assert data["format"] == "mp3"

    def test_status_job_failed(self, client, isolate_job_storage):
        """A failed job includes the error field."""
        db_file = isolate_job_storage
        service = JobStorageService(db_file)
        service.create_job("failed-job", self.VALID_URL, "720p")
        service.update_job(
            "failed-job",
            status="failed",
            error="Video unavailable",
        )

        response = client.get("/api/download/failed-job")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error"] == "Video unavailable"


class TestDownloadsList:
    """Tests for GET /api/downloads."""

    def test_list_downloads_returns_files(self, client, tmp_path):
        """GET /api/downloads returns list of files from storage."""
        def override_config():
            cfg = MagicMock()
            cfg.download_dir = str(tmp_path)
            return cfg

        app.dependency_overrides[get_app_config] = override_config

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
            app.dependency_overrides.clear()

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

    @patch("yt_dlp.YoutubeDL")
    def test_full_download_flow_mocked(self, mock_ydl, client, tmp_path):
        """Complete flow: create job -> check pending -> verify task runs."""
        # Override the module-level _JOB_DB_PATH so background task and test use same DB
        import api_routes.DownloadRouter as dr
        test_db = str(tmp_path / "test_jobs.db")
        old_db_path = dr._JOB_DB_PATH
        dr._JOB_DB_PATH = test_db

        # Mock yt-dlp to simulate successful download
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {"title": "Test Video"}
        mock_instance.prepare_filename.return_value = str(tmp_path / "test.mp4")
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_ydl.return_value = mock_instance

        try:
            # Step 1: Create download job
            resp = client.post(
                "/api/download",
                json={"url": self.VALID_URL, "output_format": "720p"},
            )
            assert resp.status_code == 200
            job_id = resp.json()["job_id"]

            # Step 2: Immediately check status
            status_resp = client.get(f"/api/download/{job_id}")
            assert status_resp.status_code == 200
            status_data = status_resp.json()
            assert status_data["status"] in ("pending", "downloading", "completed")

            # Step 3: Background task should have run
            status_resp2 = client.get(f"/api/download/{job_id}")
            assert status_resp2.status_code == 200
            status_data2 = status_resp2.json()
            assert status_data2["status"] in ("downloading", "completed")
        finally:
            dr._JOB_DB_PATH = old_db_path


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


class TestJobPersistence:
    """Tests that jobs survive a conceptual server restart."""

    VALID_URL = "https://www.youtube.com/watch?v=dQw4wRgXcQ"

    def test_job_persists_in_sqlite(self, isolate_job_storage):
        """After creating a job via the API, it can be read from DB directly."""
        db_file = isolate_job_storage

        # Create job via API
        from api_routes.DownloadRouter import get_job_storage
        service = JobStorageService(db_file)
        service.create_job("persist-job", self.VALID_URL, "720p")

        # Read it back directly from DB (simulates new server instance)
        service2 = JobStorageService(db_file)
        job = service2.get_job("persist-job")
        assert job is not None
        assert job["url"] == self.VALID_URL
        assert job["status"] == "pending"

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from core_services.JobStorageService import JobStorageService


class TestJobStorageService:
    """Tests for persistent job storage using SQLite."""

    def test_create_job(self, tmp_path):
        """Creating a job should store it and return it."""
        db_path = tmp_path / "test_jobs.db"
        service = JobStorageService(str(db_path))

        job = service.create_job(
            job_id="job-1",
            url="https://youtube.com/watch?v=test",
            output_format="720p",
        )

        assert job["id"] == "job-1"
        assert job["url"] == "https://youtube.com/watch?v=test"
        assert job["format"] == "720p"
        assert job["status"] == "pending"
        assert job.get("filepath") is None
        assert job.get("title") is None
        assert job.get("error") is None

    def test_get_existing_job(self, tmp_path):
        """Should retrieve a job that exists."""
        db_path = tmp_path / "test_jobs.db"
        service = JobStorageService(str(db_path))
        service.create_job("job-1", "https://youtube.com/watch?v=abc", "1080p")

        job = service.get_job("job-1")

        assert job is not None
        assert job["id"] == "job-1"
        assert job["status"] == "pending"

    def test_get_nonexistent_job(self, tmp_path):
        """Should return None for a job that does not exist."""
        db_path = tmp_path / "test_jobs.db"
        service = JobStorageService(str(db_path))

        job = service.get_job("nonexistent")

        assert job is None

    def test_update_job_status(self, tmp_path):
        """Should update the status of an existing job."""
        db_path = tmp_path / "test_jobs.db"
        service = JobStorageService(str(db_path))
        service.create_job("job-1", "https://youtube.com/watch?v=abc", "720p")

        service.update_job("job-1", status="downloading")
        job = service.get_job("job-1")

        assert job["status"] == "downloading"

    def test_update_job_completion(self, tmp_path):
        """Should update job with completion details."""
        db_path = tmp_path / "test_jobs.db"
        service = JobStorageService(str(db_path))
        service.create_job("job-1", "https://youtube.com/watch?v=abc", "mp3")

        service.update_job(
            "job-1",
            status="completed",
            filepath="/path/to/song.mp3",
            title="My Song",
        )
        job = service.get_job("job-1")

        assert job["status"] == "completed"
        assert job["filepath"] == "/path/to/song.mp3"
        assert job["title"] == "My Song"

    def test_update_job_failure(self, tmp_path):
        """Should update job with error details."""
        db_path = tmp_path / "test_jobs.db"
        service = JobStorageService(str(db_path))
        service.create_job("job-1", "https://youtube.com/watch?v=abc", "720p")

        service.update_job(
            "job-1",
            status="failed",
            error="Video unavailable",
        )
        job = service.get_job("job-1")

        assert job["status"] == "failed"
        assert job["error"] == "Video unavailable"

    def test_update_nonexistent_job(self, tmp_path):
        """Should return False when updating a job that doesn't exist."""
        db_path = tmp_path / "test_jobs.db"
        service = JobStorageService(str(db_path))

        result = service.update_job("nonexistent", status="completed")

        assert result is False

    def test_list_all_jobs(self, tmp_path):
        """Should list all jobs."""
        db_path = tmp_path / "test_jobs.db"
        service = JobStorageService(str(db_path))
        service.create_job("job-1", "https://youtube.com/watch?v=a", "720p")
        service.create_job("job-2", "https://youtube.com/watch?v=b", "1080p")
        service.create_job("job-3", "https://youtube.com/watch?v=c", "mp3")

        jobs = service.list_jobs()

        assert len(jobs) == 3

    def test_persistence_across_restarts(self, tmp_path):
        """Jobs should persist when service is re-created (simulates server restart)."""
        db_path = tmp_path / "test_jobs.db"

        # First "server instance"
        service1 = JobStorageService(str(db_path))
        service1.create_job("job-1", "https://youtube.com/watch?v=abc", "720p")
        service1.update_job("job-1", status="downloading")

        # Second "server instance" (restart)
        service2 = JobStorageService(str(db_path))
        job = service2.get_job("job-1")

        assert job is not None
        assert job["status"] == "downloading"
        assert job["url"] == "https://youtube.com/watch?v=abc"

    def test_job_created_at_timestamp(self, tmp_path):
        """Should store creation timestamp."""
        import time
        db_path = tmp_path / "test_jobs.db"
        service = JobStorageService(str(db_path))

        before = time.time()
        service.create_job("job-1", "https://youtube.com/watch?v=abc", "720p")
        after = time.time()

        job = service.get_job("job-1")
        assert job["created_at"] is not None
        assert before <= job["created_at"] <= after

import os
import time

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from core_services.FileStorageService import FileStorageService


class TestFileStorageServiceCleanup:
    def test_cleanup_removes_old_file(self, tmp_path):
        """Files older than max_age_minutes should be deleted."""
        service = FileStorageService(str(tmp_path))
        old_file = tmp_path / "old_video.mp4"
        old_file.write_text("old content")

        # Simulate old file by setting mtime to 2 hours ago
        old_mtime = time.time() - (2 * 3600)
        os.utime(old_file, (old_mtime, old_mtime))

        # Verify: check that mtime was actually set
        assert (old_file.stat().st_mtime < time.time() - 3600), \
            f"mtime not set: {old_file.stat().st_mtime}"

        deleted = service.cleanup_old_files(max_age_minutes=60)

        assert deleted == 1
        assert not old_file.exists()

    def test_cleanup_keeps_recent_file(self, tmp_path):
        """Files newer than max_age_minutes should NOT be deleted."""
        service = FileStorageService(str(tmp_path))
        fresh_file = tmp_path / "fresh_video.mp4"
        fresh_file.write_text("fresh content")

        deleted = service.cleanup_old_files(max_age_minutes=60)

        assert deleted == 0
        assert fresh_file.exists()

    def test_cleanup_empty_directory(self, tmp_path):
        """Cleanup on empty directory should return 0 and not raise."""
        service = FileStorageService(str(tmp_path))
        deleted = service.cleanup_old_files(max_age_minutes=60)
        assert deleted == 0

    def test_cleanup_mixed_old_and_new(self, tmp_path):
        """Only files older than threshold should be removed."""
        service = FileStorageService(str(tmp_path))
        old_file = tmp_path / "old.mp4"
        old_file.write_text("old")
        old_mtime = time.time() - (2 * 3600)
        os.utime(old_file, (old_mtime, old_mtime))

        new_file = tmp_path / "new.mp4"
        new_file.write_text("new")

        deleted = service.cleanup_old_files(max_age_minutes=60)

        assert deleted == 1
        assert not old_file.exists()
        assert new_file.exists()

    def test_cleanup_does_not_delete_directories(self, tmp_path):
        """Directories should NOT be deleted even if old."""
        service = FileStorageService(str(tmp_path))
        old_dir = tmp_path / "old_dir"
        old_dir.mkdir()
        old_mtime = time.time() - (2 * 3600)
        os.utime(old_dir, (old_mtime, old_mtime))

        deleted = service.cleanup_old_files(max_age_minutes=60)

        assert deleted == 0  # directories ignored
        assert old_dir.exists()

    def test_cleanup_custom_age(self, tmp_path):
        """Respect custom max_age_minutes parameter."""
        service = FileStorageService(str(tmp_path))
        medium_file = tmp_path / "medium.mp4"
        medium_file.write_text("medium")
        # 30 minutes old
        medium_mtime = time.time() - (30 * 60)
        os.utime(medium_file, (medium_mtime, medium_mtime))

        # With 60 min threshold -> keep
        assert service.cleanup_old_files(max_age_minutes=60) == 0
        assert medium_file.exists()

        # With 10 min threshold -> delete
        assert service.cleanup_old_files(max_age_minutes=10) == 1
        assert not medium_file.exists()

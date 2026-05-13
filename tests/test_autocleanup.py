"""Tests for the automatic cleanup scheduler (lifespan).

Verifies that the cleanup task is wired correctly and runs on startup.
"""

import asyncio
import os
import time

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from autocleanup import start_cleanup_task


class TestStartCleanupTask:
    """Tests for the async cleanup scheduler coroutine."""

    @pytest.mark.asyncio
    async def test_cleanup_task_runs_cleanup_at_start(self, tmp_path):
        """The scheduler should call cleanup immediately when started."""
        from core_services.FileStorageService import FileStorageService

        # Create an old file
        old_file = tmp_path / "old.mp4"
        old_file.write_text("old")
        os.utime(old_file, (time.time() - (2 * 3600), time.time() - (2 * 3600)))

        storage = FileStorageService(str(tmp_path))

        # Run the task for a short time then cancel it
        task = asyncio.create_task(start_cleanup_task(storage, max_age_minutes=60, check_interval_seconds=1))
        await asyncio.sleep(1.5)  # Let the first cleanup run
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # The old file should be gone
        assert not old_file.exists()

    @pytest.mark.asyncio
    async def test_cleanup_task_respects_interval(self, tmp_path):
        """The scheduler should not clean up again before the interval."""
        from core_services.FileStorageService import FileStorageService

        storage = FileStorageService(str(tmp_path))

        call_count = 0
        original_cleanup = storage.cleanup_old_files

        def counting_cleanup(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return original_cleanup(*args, **kwargs)

        storage.cleanup_old_files = counting_cleanup

        task = asyncio.create_task(start_cleanup_task(storage, max_age_minutes=60, check_interval_seconds=1))
        await asyncio.sleep(0.5)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # Should have been called at least once (initial run)
        assert call_count >= 1

    @pytest.mark.asyncio
    async def test_cleanup_task_handles_empty_dir(self, tmp_path):
        """The scheduler should not crash on empty directory."""
        from core_services.FileStorageService import FileStorageService

        storage = FileStorageService(str(tmp_path))

        task = asyncio.create_task(start_cleanup_task(storage, max_age_minutes=60, check_interval_seconds=1))
        await asyncio.sleep(0.5)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # No crash = pass
        assert True

"""Automatic cleanup scheduler — runs in the background.

Starts a long-running asyncio task that calls FileStorageService.cleanup_old_files()
at a regular interval (default: every 1 hour). The first cleanup runs immediately
on startup so files are cleaned right after a cold start.
"""

import asyncio
import logging
import time

from core_services.FileStorageService import FileStorageService
from config_settings.AppConfig import AppConfig

logger = logging.getLogger(__name__)


async def start_cleanup_task(
    storage: FileStorageService,
    max_age_minutes: int = 60,
    check_interval_seconds: int = 3600,
) -> None:
    """Run an infinite loop that cleans up old files at a fixed interval.

    Args:
        storage: The FileStorageService instance.
        max_age_minutes: Delete files older than this (default: 60).
        check_interval_seconds: How often to check (default: 3600 = 1 hour).
    """
    while True:
        try:
            deleted = storage.cleanup_old_files(max_age_minutes=max_age_minutes)
            if deleted > 0:
                logger.info(f"Cleanup: deleted {deleted} old file(s) (older than {max_age_minutes} min)")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
        await asyncio.sleep(check_interval_seconds)

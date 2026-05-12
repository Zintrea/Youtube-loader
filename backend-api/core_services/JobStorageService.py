import sqlite3
import time
from typing import Dict, Optional, List, Any
from pathlib import Path


class JobStorageService:
    """Persistent job storage for download jobs using SQLite."""

    def __init__(self, db_path: str):
        """Initialize with path to SQLite database file.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    format TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    filepath TEXT,
                    title TEXT,
                    error TEXT,
                    created_at REAL NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def create_job(
        self,
        job_id: str,
        url: str,
        output_format: str,
    ) -> Dict[str, Any]:
        """Create a new download job with pending status.

        Args:
            job_id: Unique job identifier.
            url: YouTube video URL.
            output_format: Requested format (1080p, 720p, mp3, etc.).

        Returns:
            Dict with the created job data.
        """
        now = time.time()
        conn = self._get_conn()
        try:
            conn.execute(
                """
                INSERT INTO jobs (id, url, format, status, created_at)
                VALUES (?, ?, ?, 'pending', ?)
                """,
                (job_id, url, output_format, now),
            )
            conn.commit()
        finally:
            conn.close()

        return {
            "id": job_id,
            "url": url,
            "format": output_format,
            "status": "pending",
            "filepath": None,
            "title": None,
            "error": None,
            "created_at": now,
        }

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a job by ID.

        Args:
            job_id: Unique job identifier.

        Returns:
            Dict with job data, or None if not found.
        """
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM jobs WHERE id = ?", (job_id,)
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return self._row_to_dict(row)

    def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        filepath: Optional[str] = None,
        title: Optional[str] = None,
        error: Optional[str] = None,
    ) -> bool:
        """Update fields of an existing job.

        Args:
            job_id: Unique job identifier.
            status: New status (e.g. 'downloading', 'completed', 'failed').
            filepath: Path to the downloaded file.
            title: Video title.
            error: Error message if failed.

        Returns:
            True if the job was updated, False if not found.
        """
        conn = self._get_conn()
        try:
            existing = conn.execute(
                "SELECT id FROM jobs WHERE id = ?", (job_id,)
            ).fetchone()
            if existing is None:
                return False

            fields = []
            values = []
            if status is not None:
                fields.append("status = ?")
                values.append(status)
            if filepath is not None:
                fields.append("filepath = ?")
                values.append(filepath)
            if title is not None:
                fields.append("title = ?")
                values.append(title)
            if error is not None:
                fields.append("error = ?")
                values.append(error)

            if fields:
                values.append(job_id)
                sql = f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?"
                conn.execute(sql, values)
                conn.commit()
            return True
        finally:
            conn.close()

    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all jobs.

        Returns:
            List of job dicts, ordered by creation time (newest first).
        """
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC"
            ).fetchall()
        finally:
            conn.close()

        return [self._row_to_dict(row) for row in rows]

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        return dict(row)

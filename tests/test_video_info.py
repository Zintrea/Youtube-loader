import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from fastapi.testclient import TestClient
from Main import app


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


class TestVideoInfoEndpoint:
    """Tests for GET /api/video-info endpoint."""

    VALID_URL = "https://www.youtube.com/watch?v=dQw4wRgXcQ"
    SHORT_URL = "https://youtu.be/dQw4wRgXcQ"

    @patch("yt_dlp.YoutubeDL")
    def test_video_info_returns_metadata(self, mock_ydl, client):
        """GET /api/video-info with valid URL returns video metadata."""
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            "title": "Test Video Title",
            "duration": 120,
            "thumbnail": "https://img.youtube.com/vi/test/maxresdefault.jpg",
            "formats": [{"format_id": "137", "ext": "mp4", "height": 1080}],
        }
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_ydl.return_value = mock_instance

        response = client.get(f"/api/video-info?url={self.VALID_URL}")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Video Title"
        assert data["duration"] == 120
        assert "thumbnail" in data
        assert "error" not in data or data["error"] is None

    @patch("yt_dlp.YoutubeDL")
    def test_video_info_returns_short_url(self, mock_ydl, client):
        """GET /api/video-info accepts youtu.be short URLs."""
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            "title": "Short URL Video",
            "duration": 60,
            "thumbnail": "https://example.com/thumb.jpg",
        }
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_ydl.return_value = mock_instance

        response = client.get(f"/api/video-info?url={self.SHORT_URL}")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Short URL Video"

    @patch("yt_dlp.YoutubeDL")
    def test_video_info_no_formats_key(self, mock_ydl, client):
        """GET /api/video-info handles response without formats key."""
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            "title": "No Formats Video",
            "duration": 45,
            "thumbnail": "https://example.com/thumb.jpg",
        }
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_ydl.return_value = mock_instance

        response = client.get(f"/api/video-info?url={self.VALID_URL}")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "No Formats Video"
        assert data["duration"] == 45

    @patch("yt_dlp.YoutubeDL")
    def test_video_info_error_returns_error_field(self, mock_ydl, client):
        """GET /api/video-info returns error field when yt-dlp fails."""
        mock_instance = MagicMock()
        mock_instance.__enter__ = MagicMock(side_effect=Exception("Video unavailable"))
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_ydl.return_value = mock_instance

        response = client.get(f"/api/video-info?url={self.VALID_URL}")

        assert response.status_code == 200
        data = response.json()
        assert data["error"] == "Video unavailable"

    def test_video_info_missing_url_returns_422(self, client):
        """GET /api/video-info without url param returns 422."""
        response = client.get("/api/video-info")
        assert response.status_code == 422

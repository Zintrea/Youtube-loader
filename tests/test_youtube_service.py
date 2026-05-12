import pytest
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from core_services.YoutubeService import YoutubeService


class TestYoutubeServiceInstantiation:
    def test_singleton_pattern(self):
        s1 = YoutubeService()
        s2 = YoutubeService()
        assert s1 is s2

    def test_instance_not_none(self):
        service = YoutubeService()
        assert service is not None


class TestGetFormatOpts:
    def setup_method(self):
        self.service = YoutubeService()

    def test_1080p_format(self):
        opts = self.service._get_format_opts("1080p")
        assert opts["format"] == (
            "bestvideo[vcodec^=avc1][height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        )
        assert opts["merge_output_format"] == "mp4"

    def test_720p_format(self):
        opts = self.service._get_format_opts("720p")
        assert opts["format"] == (
            "bestvideo[vcodec^=avc1][height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        )
        assert opts["merge_output_format"] == "mp4"

    def test_480p_format(self):
        opts = self.service._get_format_opts("480p")
        assert opts["format"] == (
            "bestvideo[vcodec^=avc1][height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        )
        assert opts["merge_output_format"] == "mp4"

    def test_mp3_format(self):
        opts = self.service._get_format_opts("mp3")
        assert opts["format"] == "bestaudio/best"
        assert "postprocessors" in opts
        pp = opts["postprocessors"][0]
        assert pp["key"] == "FFmpegExtractAudio"
        assert pp["preferredcodec"] == "mp3"
        assert pp["preferredquality"] == "320"
        assert "merge_output_format" not in opts

    def test_m4a_format(self):
        opts = self.service._get_format_opts("m4a")
        assert opts["format"] == "bestaudio[ext=m4a]/bestaudio"
        assert "postprocessors" in opts
        pp = opts["postprocessors"][0]
        assert pp["key"] == "FFmpegExtractAudio"
        assert pp["preferredcodec"] == "m4a"
        assert "merge_output_format" not in opts

    def test_unknown_format_defaults_to_720p(self):
        opts = self.service._get_format_opts("unknown")
        assert opts["format"] == (
            "bestvideo[vcodec^=avc1][height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        )
        assert opts["merge_output_format"] == "mp4"


class TestGetVideoInfo:
    def setup_method(self):
        self.service = YoutubeService()

    def test_error_on_invalid_url(self):
        """get_video_info returns an error dict for invalid URLs."""
        result = self.service.get_video_info("https://youtube.com/watch?v=notarealvideo")
        assert "error" in result
        assert isinstance(result["error"], str)
        assert len(result["error"]) > 0

    def test_error_on_empty_url(self):
        result = self.service.get_video_info("")
        assert "error" in result

    def test_error_on_malformed_url(self):
        result = self.service.get_video_info("not-a-url")
        assert "error" in result

    @patch("core_services.YoutubeService.yt_dlp")
    def test_successful_video_info(self, mock_yt_dlp):
        """Test get_video_info returns the expected structure on success."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {
            "title": "Test Video",
            "duration": 120,
            "thumbnail": "https://example.com/thumb.jpg",
            "formats": [
                {"format_id": "1", "ext": "mp4", "height": 1080},
                {"format_id": "2", "ext": "webm", "abr": 128},
            ],
        }
        mock_yt_dlp.YoutubeDL.return_value = mock_ydl

        result = self.service.get_video_info("https://youtube.com/watch?v=abc123")

        assert "error" not in result
        assert result["title"] == "Test Video"
        assert result["duration"] == 120
        assert result["thumbnail"] == "https://example.com/thumb.jpg"
        assert len(result["formats"]) == 2
        assert result["formats"][0]["format_id"] == "1"
        assert result["formats"][0]["ext"] == "mp4"
        assert result["formats"][0]["quality"] == 1080

    @patch("core_services.YoutubeService.yt_dlp")
    def test_video_info_no_formats_key(self, mock_yt_dlp):
        """Test when video info has no formats key."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {
            "title": "No Formats",
            "duration": 60,
            "thumbnail": None,
        }
        mock_yt_dlp.YoutubeDL.return_value = mock_ydl

        result = self.service.get_video_info("https://youtube.com/watch?v=nope")

        assert "error" not in result
        assert result["formats"] == []

    @patch("core_services.YoutubeService.yt_dlp")
    def test_video_info_exception_returns_error(self, mock_yt_dlp):
        """Test that exceptions during extract_info return an error dict."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.side_effect = Exception("Connection error")
        mock_yt_dlp.YoutubeDL.return_value = mock_ydl

        result = self.service.get_video_info("https://youtube.com/watch?v=fail")

        assert "error" in result
        assert "Connection error" in result["error"]

    @patch("core_services.YoutubeService.yt_dlp")
    def test_video_info_ytdl_exception(self, mock_yt_dlp):
        """Test that YoutubeDL construction errors are caught."""
        mock_yt_dlp.YoutubeDL.side_effect = Exception("Bad config")

        result = self.service.get_video_info("https://youtube.com/watch?v=xyz")

        assert "error" in result


class TestDownloadVideo:
    def setup_method(self):
        self.service = YoutubeService()

    @patch("core_services.YoutubeService.yt_dlp")
    def test_successful_download_mp4(self, mock_yt_dlp, tmp_path):
        """Test successful video download returns correct dict."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {
            "title": "Test Video",
            "id": "abc123",
        }
        mock_ydl.prepare_filename.return_value = str(tmp_path / "Test Video.mp4")
        mock_yt_dlp.YoutubeDL.return_value = mock_ydl

        result = self.service.download_video(
            "https://youtube.com/watch?v=abc123", "720p", str(tmp_path)
        )

        assert result["success"] is True
        assert "filepath" in result
        assert result["title"] == "Test Video"

    @patch("core_services.YoutubeService.yt_dlp")
    def test_successful_download_mp3(self, mock_yt_dlp, tmp_path):
        """Audio-only mp3 download returns correct filepath."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {
            "title": "Music Track",
            "id": "mus1c",
        }
        mock_ydl.prepare_filename.return_value = str(tmp_path / "Music Track.webm")
        mock_yt_dlp.YoutubeDL.return_value = mock_ydl

        result = self.service.download_video(
            "https://youtube.com/watch?v=music123", "mp3", str(tmp_path)
        )

        assert result["success"] is True
        assert result["filepath"].endswith(".mp3")

    @patch("core_services.YoutubeService.yt_dlp")
    def test_successful_download_m4a(self, mock_yt_dlp, tmp_path):
        """Audio-only m4a download returns correct filepath."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {
            "title": "Podcast",
            "id": "pod1",
        }
        mock_ydl.prepare_filename.return_value = str(tmp_path / "Podcast.webm")
        mock_yt_dlp.YoutubeDL.return_value = mock_ydl

        result = self.service.download_video(
            "https://youtube.com/watch?v=pod123", "m4a", str(tmp_path)
        )

        assert result["success"] is True
        assert result["filepath"].endswith(".m4a")

    @patch("core_services.YoutubeService.yt_dlp")
    def test_download_error_returns_failure(self, mock_yt_dlp, tmp_path):
        """Download failure returns dict with success=False and error message."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.side_effect = Exception("Video unavailable")
        mock_yt_dlp.YoutubeDL.return_value = mock_ydl

        result = self.service.download_video(
            "https://youtube.com/watch?v=missing", "720p", str(tmp_path)
        )

        assert result["success"] is False
        assert "error" in result
        assert "Video unavailable" in result["error"]

    @patch("core_services.YoutubeService.yt_dlp")
    def test_download_passes_correct_format_opts(self, mock_yt_dlp, tmp_path):
        """Verify format options are merged correctly for mp3 download."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {"title": "Song", "id": "1"}
        mock_ydl.prepare_filename.return_value = str(tmp_path / "Song.opus")
        mock_yt_dlp.YoutubeDL.return_value = mock_ydl

        self.service.download_video(
            "https://youtube.com/watch?v=song1", "mp3", str(tmp_path)
        )

        call_kwargs = mock_yt_dlp.YoutubeDL.call_args[0][0]
        assert call_kwargs["format"] == "bestaudio/best"
        assert "merge_output_format" not in call_kwargs  # not set by mp3
        assert "postprocessors" in call_kwargs

    @patch("core_services.YoutubeService.yt_dlp")
    def test_download_passes_correct_format_opts_1080p(self, mock_yt_dlp, tmp_path):
        """Verify 1080p format options are passed correctly."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {"title": "4K Video", "id": "1"}
        mock_ydl.prepare_filename.return_value = str(tmp_path / "4K Video.mkv")
        mock_yt_dlp.YoutubeDL.return_value = mock_ydl

        self.service.download_video(
            "https://youtube.com/watch?v=4k123", "1080p", str(tmp_path)
        )

        call_kwargs = mock_yt_dlp.YoutubeDL.call_args[0][0]
        assert "height<=1080" in call_kwargs["format"]
        assert call_kwargs["merge_output_format"] == "mp4"

    @patch("core_services.YoutubeService.yt_dlp")
    def test_download_error_on_ytdl_construction(self, mock_yt_dlp, tmp_path):
        """If YoutubeDL constructor raises, returns failure dict."""
        mock_yt_dlp.YoutubeDL.side_effect = Exception("Config error")

        result = self.service.download_video(
            "https://youtube.com/watch?v=x", "720p", str(tmp_path)
        )

        assert result["success"] is False
        assert "error" in result

    def test_download_invalid_url_no_mock(self):
        """Without mock, invalid URL should return failure dict."""
        result = self.service.download_video(
            "https://youtube.com/watch?v=fake123", "720p", "/tmp/test_dl"
        )
        assert result["success"] is False
        assert "error" in result

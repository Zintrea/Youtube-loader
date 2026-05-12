from typing import Dict, Optional


import yt_dlp
from typing import Dict, Optional, Any


class YoutubeService:
    _instance: Optional["YoutubeService"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_common_opts(self, output_dir: str) -> Dict[str, Any]:
        return {
            "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
        }

    def _get_format_opts(self, output_format: str) -> Dict[str, Any]:
        """Maps format strings to yt-dlp options."""
        opts = {}
        if output_format == "1080p":
            opts["format"] = (
                "bestvideo[vcodec^=avc1][height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            )
            opts["merge_output_format"] = "mp4"
        elif output_format == "720p":
            opts["format"] = (
                "bestvideo[vcodec^=avc1][height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            )
            opts["merge_output_format"] = "mp4"
        elif output_format == "480p":
            opts["format"] = (
                "bestvideo[vcodec^=avc1][height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            )
            opts["merge_output_format"] = "mp4"
        elif output_format == "mp3":
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ]
        elif output_format == "m4a":
            opts["format"] = "bestaudio[ext=m4a]/bestaudio"
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ]
        else:
            # Default to 720p if unknown
            opts["format"] = (
                "bestvideo[vcodec^=avc1][height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            )
            opts["merge_output_format"] = "mp4"
        return opts

    def get_video_info(self, url: str) -> Dict:
        """Retrieve metadata for a YouTube video.

        Args:
            url: The YouTube video URL.

        Returns:
            Dict with keys: title, duration, thumbnail, formats.
            On error, returns {"error": "message"}.
        """
        ydl_opts = {"quiet": True, "no_warnings": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = [
                    {
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext"),
                        "quality": f.get("height") or f.get("abr"),
                    }
                    for f in info.get("formats", [])
                ]
                return {
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                    "formats": formats,
                }
        except Exception as e:
            return {"error": str(e)}

    def download_video(self, url: str, output_format: str, output_dir: str) -> Dict:
        """Download a YouTube video with the specified format.

        Args:
            url: The YouTube video URL.
            output_format: Desired format (1080p, 720p, 480p, mp3, m4a).
            output_dir: Directory to save the downloaded file.

        Returns:
            Dict with keys: success, filepath, title.
        """
        ydl_opts = self._get_common_opts(output_dir)
        ydl_opts.update(self._get_format_opts(output_format))

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # If it was merged or post-processed, the extension might have changed
                if output_format == "mp3":
                    filename = filename.rsplit(".", 1)[0] + ".mp3"
                elif output_format == "m4a":
                    filename = filename.rsplit(".", 1)[0] + ".m4a"
                elif "mp4" in ydl_opts.get("merge_output_format", ""):
                    filename = filename.rsplit(".", 1)[0] + ".mp4"

                return {
                    "success": True,
                    "filepath": filename,
                    "title": info.get("title"),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

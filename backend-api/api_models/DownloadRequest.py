from typing import Optional, List

from pydantic import BaseModel, field_validator


ALLOWED_FORMATS = {"1080p", "720p", "480p", "mp3", "m4a"}


class DownloadRequest(BaseModel):
    """Request model for initiating a YouTube download."""

    url: str
    output_format: str = "720p"
    custom_filename: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        if "youtube.com" not in v and "youtu.be" not in v:
            raise ValueError("URL must be a valid YouTube URL (youtube.com or youtu.be)")
        return v

    @field_validator("output_format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if v not in ALLOWED_FORMATS:
            allowed = ", ".join(sorted(ALLOWED_FORMATS))
            raise ValueError(
                f"output_format must be one of: {allowed}. Got: {v}"
            )
        return v


class DownloadResponse(BaseModel):
    """Response returned when a download job is accepted."""

    job_id: str
    status: str


class StatusResponse(BaseModel):
    """Response returned when querying a download job's status."""

    url: Optional[str] = None
    status: str
    format: Optional[str] = None
    filepath: Optional[str] = None
    title: Optional[str] = None
    error: Optional[str] = None


class VideoInfoResponse(BaseModel):
    """Response returned when retrieving video metadata."""

    title: Optional[str] = None
    duration: Optional[int] = None
    thumbnail: Optional[str] = None
    formats: Optional[List[dict]] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Generic error response."""

    detail: str
    code: Optional[int] = None

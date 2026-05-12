import os
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from api_models.DownloadRequest import (
    DownloadRequest,
    DownloadResponse,
    StatusResponse,
    ErrorResponse,
)
from config_settings.AppConfig import AppConfig
from core_services.YoutubeService import YoutubeService
from core_services.JobStorageService import JobStorageService
from core_services.FileStorageService import FileStorageService

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency setup
# ---------------------------------------------------------------------------

_JOB_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "jobs.db",
)

# Global variable for test overrides / production flexibility
_job_storage_override: JobStorageService | None = None


def get_youtube_service() -> YoutubeService:
    return YoutubeService()


def get_app_config() -> AppConfig:
    return AppConfig()


def get_storage_service(
    config: AppConfig = Depends(get_app_config),
) -> FileStorageService:
    return FileStorageService(config.download_dir)


def get_job_storage() -> JobStorageService:
    return JobStorageService(_JOB_DB_PATH)


# ---------------------------------------------------------------------------
# Background task
# ---------------------------------------------------------------------------

async def run_download_task(
    job_id: str,
    url: str,
    output_format: str,
    output_dir: str,
    yt_service: YoutubeService,
    db_path: str,
) -> None:
    job_storage = JobStorageService(db_path)
    job_storage.update_job(job_id, status="downloading")

    result = yt_service.download_video(url, output_format, output_dir)
    if result["success"]:
        job_storage.update_job(
            job_id,
            status="completed",
            filepath=result["filepath"],
            title=result["title"],
        )
    else:
        job_storage.update_job(
            job_id,
            status="failed",
            error=result.get("error"),
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post(
    "/download",
    response_model=DownloadResponse,
    responses={422: {"model": ErrorResponse, "description": "Validation error"}},
)
async def start_download(
    request: DownloadRequest,
    background_tasks: BackgroundTasks,
    yt_service: YoutubeService = Depends(get_youtube_service),
    config: AppConfig = Depends(get_app_config),
    job_storage: JobStorageService = Depends(get_job_storage),
) -> DownloadResponse:
    """Start downloading a YouTube video."""
    job_id = str(uuid.uuid4())

    job_storage.create_job(
        job_id=job_id,
        url=request.url,
        output_format=request.output_format,
    )

    background_tasks.add_task(
        run_download_task,
        job_id,
        request.url,
        request.output_format,
        config.download_dir,
        yt_service,
        _JOB_DB_PATH,
    )

    return DownloadResponse(job_id=job_id, status="pending")


@router.get(
    "/download/{job_id}",
    response_model=StatusResponse,
    responses={404: {"model": ErrorResponse, "description": "Job not found"}},
)
async def get_download_status(
    job_id: str,
    job_storage: JobStorageService = Depends(get_job_storage),
) -> StatusResponse:
    """Get the download status for a given job ID."""
    job = job_storage.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                detail="Download job not found", code=404
            ).model_dump(),
        )
    return StatusResponse(
        url=job.get("url"),
        status=job.get("status"),
        format=job.get("format"),
        filepath=job.get("filepath"),
        title=job.get("title"),
        error=job.get("error"),
    )


@router.get("/downloads")
async def list_downloads(
    storage_service: FileStorageService = Depends(get_storage_service),
) -> dict[str, Any]:
    """List all downloaded files."""
    return {"files": storage_service.list_files()}


@router.get("/video-info")
async def get_video_info(
    url: str,
    yt_service: YoutubeService = Depends(get_youtube_service),
) -> dict[str, Any]:
    """Retrieve metadata for a YouTube video (title, duration, thumbnail)."""
    info = yt_service.get_video_info(url)
    return info

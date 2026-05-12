from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from typing import Dict, Any
import uuid

from core_services.YoutubeService import YoutubeService
from core_services.FileStorageService import FileStorageService
from config_settings.AppConfig import AppConfig
from api_models.DownloadRequest import (
    DownloadRequest,
    DownloadResponse,
    StatusResponse,
    ErrorResponse,
)

router = APIRouter()

# In-memory storage for download jobs (simplified for Phase 1.1)
download_jobs: Dict[str, Dict[str, Any]] = {}


def get_youtube_service():
    return YoutubeService()


def get_app_config():
    return AppConfig()


def get_storage_service(config: AppConfig = Depends(get_app_config)):
    return FileStorageService(config.download_dir)


async def run_download_task(
    job_id: str,
    url: str,
    output_format: str,
    output_dir: str,
    yt_service: YoutubeService,
):
    download_jobs[job_id]["status"] = "downloading"
    result = yt_service.download_video(url, output_format, output_dir)
    if result["success"]:
        download_jobs[job_id]["status"] = "completed"
        download_jobs[job_id]["filepath"] = result["filepath"]
        download_jobs[job_id]["title"] = result["title"]
    else:
        download_jobs[job_id]["status"] = "failed"
        download_jobs[job_id]["error"] = result.get("error")


@router.post(
    "/download",
    response_model=DownloadResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def start_download(
    request: DownloadRequest,
    background_tasks: BackgroundTasks,
    yt_service: YoutubeService = Depends(get_youtube_service),
    config: AppConfig = Depends(get_app_config),
):
    """Start downloading a YouTube video."""
    job_id = str(uuid.uuid4())
    download_jobs[job_id] = {
        "id": job_id,
        "url": request.url,
        "format": request.output_format,
        "status": "pending",
    }

    background_tasks.add_task(
        run_download_task,
        job_id,
        request.url,
        request.output_format,
        config.download_dir,
        yt_service,
    )

    return DownloadResponse(job_id=job_id, status="pending")


@router.get(
    "/download/{job_id}",
    response_model=StatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
    },
)
async def get_download_status(job_id: str):
    """Get the download status for a given job ID."""
    if job_id not in download_jobs:
        raise HTTPException(
            status_code=404, detail=ErrorResponse(detail="Download job not found", code=404).model_dump()
        )
    job = download_jobs[job_id]
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
):
    """List all downloaded files."""
    return {"files": storage_service.list_files()}

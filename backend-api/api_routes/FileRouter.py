from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from core_services.FileStorageService import FileStorageService
from config_settings.AppConfig import AppConfig

router = APIRouter()


def get_app_config():
    return AppConfig()


def get_storage_service(config: AppConfig = Depends(get_app_config)):
    return FileStorageService(config.download_dir)


@router.get("/files")
async def list_files(
    storage_service: FileStorageService = Depends(get_storage_service),
):
    """List all downloaded files."""
    return {"files": storage_service.list_files()}


@router.get("/files/{filename}")
async def download_file(
    filename: str,
    storage_service: FileStorageService = Depends(get_storage_service),
):
    """Download/serve a specific file."""
    file_path = Path(storage_service.base_dir) / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(file_path), filename=filename)


@router.delete("/files/{filename}")
async def delete_file(
    filename: str,
    storage_service: FileStorageService = Depends(get_storage_service),
):
    """Delete a specific file."""
    deleted = storage_service.delete_file(filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": f"File {filename} deleted"}


@router.post("/cleanup")
async def cleanup_old_files(
    config: AppConfig = Depends(get_app_config),
    storage_service: FileStorageService = Depends(get_storage_service),
):
    """Delete downloaded files older than the configured max age."""
    files_before = storage_service.list_files()
    total_before = len(files_before)

    deleted_count = storage_service.cleanup_old_files(max_age_minutes=config.cleanup_max_age)

    files_after = storage_service.list_files()

    return {
        "deleted_count": deleted_count,
        "total_files_before": total_before,
        "total_files_after": len(files_after),
    }

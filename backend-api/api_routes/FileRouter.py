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

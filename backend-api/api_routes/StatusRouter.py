from fastapi import APIRouter
from pydantic import BaseModel

from api_models.DownloadRequest import ErrorResponse

router = APIRouter()


class StatusOkResponse(BaseModel):
    status: str
    version: str


@router.get(
    "/status",
    response_model=StatusOkResponse,
)
async def get_status():
    """Return API status information."""
    return {"status": "ok", "version": "0.1.0"}

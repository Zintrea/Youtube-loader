import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config_settings.AppConfig import AppConfig
from core_services.FileStorageService import FileStorageService
from autocleanup import start_cleanup_task

from api_routes.DownloadRouter import router as download_router
from api_routes.FileRouter import router as file_router
from api_routes.StatusRouter import router as status_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run cleanup scheduler in the background when the app starts."""
    config = AppConfig()
    storage = FileStorageService(config.download_dir)
    cleanup_task = asyncio.create_task(start_cleanup_task(storage, config.cleanup_max_age))
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Youtube-loader API", version="0.1.0", lifespan=lifespan)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(download_router, prefix="/api")
app.include_router(file_router, prefix="/api")
app.include_router(status_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Main:app", host="0.0.0.0", port=8000, reload=True)

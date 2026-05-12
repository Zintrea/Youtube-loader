from fastapi import FastAPI

from api_routes.DownloadRouter import router as download_router
from api_routes.StatusRouter import router as status_router

app = FastAPI(title="Youtube-loader API", version="0.1.0")

# Include routers
app.include_router(download_router, prefix="/api")
app.include_router(status_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

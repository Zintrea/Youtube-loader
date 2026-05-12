from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_routes.DownloadRouter import router as download_router
from api_routes.FileRouter import router as file_router
from api_routes.StatusRouter import router as status_router

app = FastAPI(title="Youtube-loader API", version="0.1.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

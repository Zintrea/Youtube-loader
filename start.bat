@echo off
echo ============================================
echo   YouTube Loader - Starting Dev Servers
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] Starting Backend (FastAPI on port 8000)...
start "Backend - YouTube Loader" cmd /c "cd backend-api && ..\venv\Scripts\python.exe Main.py"
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend (Next.js on port 3000)...
start "Frontend - YouTube Loader" cmd /c "cd frontend-web && npm run dev"

echo.
echo ============================================
echo   Both servers starting!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo ============================================
echo.
echo   Press any key to stop both servers...
pause >nul

taskkill /FI "WindowTitle eq Backend - YouTube Loader" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Frontend - YouTube Loader" /T /F >nul 2>&1
echo Servers stopped.

@echo off
echo ========================================================
echo   MediEvidence AI - Unified System Startup
echo ========================================================
echo.

echo [1/3] Terminating any stale processes on ports 3000/8000...
powershell -Command "$p3000 = (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue).OwningProcess; if ($p3000) { Stop-Process -Id $p3000 -Force -ErrorAction SilentlyContinue }"
powershell -Command "$p8000 = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess; if ($p8000) { Stop-Process -Id $p8000 -Force -ErrorAction SilentlyContinue }"

echo [2/3] Starting Backend Server (FastAPI on Port 8000)...
start "MediEvidence AI Backend" cmd /c "start_backend.bat"

echo [3/3] Starting Frontend Web App (Next.js on Port 3000)...
start "MediEvidence AI Frontend" cmd /c "start_frontend.bat"

echo.
echo ========================================================
echo   Both services are starting!
echo   - Web UI: http://localhost:3000
echo   - Backend Docs: http://localhost:8000/docs
echo ========================================================
echo.
timeout /t 5


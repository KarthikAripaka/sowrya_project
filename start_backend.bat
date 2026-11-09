@echo off
title MediEvidence AI - FastAPI Backend (Port 8000)
echo ========================================================
echo   MediEvidence AI - FastAPI Backend Server
echo ========================================================
echo.
echo Starting FastAPI with multi-key Groq pool on http://127.0.0.1:8000 ...
echo API Documentation: http://127.0.0.1:8000/docs
echo.

set PYTHONPATH=%CD%
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause

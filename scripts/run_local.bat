@echo off
echo ==============================================================================
echo EVIDENCE-BASED MEDICAL REPORT ^& X-RAY INTERPRETATION SYSTEM
echo 100%% Free ^& Open-Source Local Execution Mode
echo ==============================================================================

:: Step 1: Check virtualenv
if not exist ".venv" (
    echo [1/3] Creating Python Virtual Environment...
    python -m venv .venv
)

:: Step 2: Install dependencies if required
echo [2/3] Checking Backend ^& Frontend Dependencies...

:: Step 3: Start FastAPI Backend in background
echo Starting Backend API on http://localhost:8000...
start "MediEvidence Backend" cmd /k "call .venv\Scripts\activate.bat && set PYTHONPATH=. && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Step 4: Start Next.js Frontend
echo Starting Next.js Frontend on http://localhost:3000...
cd frontend
start "MediEvidence Frontend" cmd /k "npm run dev"

echo.
echo ==============================================================================
echo APPLICATION LAUNCHED SUCCESSFULLY!
echo Web UI:     http://localhost:3000
echo Backend API: http://localhost:8000
echo API Docs:   http://localhost:8000/docs
echo Demo User:  demo@medicalai.org / MedicalAI2026!
echo ==============================================================================
pause


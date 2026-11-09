#!/usr/bin/env bash
set -e

echo "=============================================================================="
echo "EVIDENCE-BASED MEDICAL REPORT & X-RAY INTERPRETATION SYSTEM"
echo "100% Free & Open-Source Local Execution Mode"
echo "=============================================================================="

# Check Python environment
if [ ! -d ".venv" ]; then
    echo "[1/3] Creating Python Virtual Environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r backend/requirements.txt
else
    source .venv/bin/activate
fi

# Check Node environment
if [ ! -d "frontend/node_modules" ]; then
    echo "[2/3] Installing Frontend Dependencies..."
    cd frontend && npm install && cd ..
fi

echo "[3/3] Launching Local Services..."
export PYTHONPATH=.
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd frontend && npm run dev &
FRONTEND_PID=$!

echo "=============================================================================="
echo "APPLICATION RUNNING:"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Demo Login: demo@medicalai.org / MedicalAI2026!"
echo "=============================================================================="

wait $BACKEND_PID $FRONTEND_PID


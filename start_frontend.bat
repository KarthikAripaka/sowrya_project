@echo off
title MediEvidence AI - Next.js Frontend (Port 3000)
echo ========================================================
echo   MediEvidence AI - Next.js Frontend Web Application
echo ========================================================
echo.
cd frontend

echo Checking for stale .next build cache...
if exist ".next" (
    echo Refreshing dev cache...
    powershell -Command "Remove-Item -Recurse -Force '.next' -ErrorAction SilentlyContinue"
)

echo Starting Next.js Dev Server on http://localhost:3000 ...
echo (Tip: Press Ctrl + F5 in your browser on first load to bypass old cached CSS)
echo.

npm run dev
pause


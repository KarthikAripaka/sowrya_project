@echo off
echo ========================================================
echo   MediEvidence AI - Clean Environment & Port Reset
echo ========================================================
echo.

echo [1/3] Terminating any lingering processes on ports 3000 and 8000...
powershell -Command "Get-Process node, python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"
powershell -Command "$p3000 = (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue).OwningProcess; if ($p3000) { Stop-Process -Id $p3000 -Force -ErrorAction SilentlyContinue }"
powershell -Command "$p8000 = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess; if ($p8000) { Stop-Process -Id $p8000 -Force -ErrorAction SilentlyContinue }"

echo [2/3] Cleaning stale Next.js cache in frontend/.next...
if exist "frontend\.next" (
    powershell -Command "Remove-Item -Recurse -Force 'frontend\.next' -ErrorAction SilentlyContinue"
)

echo [3/3] Ports 3000 and 8000 are completely free!
echo Environment is clean and ready to launch.
echo.
pause


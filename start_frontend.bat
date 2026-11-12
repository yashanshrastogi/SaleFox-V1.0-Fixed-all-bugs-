@echo off
title SaleFox - Frontend UI
cd /d "%~dp0"

echo ========================================================
echo Starting SaleFox React Frontend on Port 5173...
echo Working Directory: %CD%
echo ========================================================

if not exist "node_modules" (
    echo [ERROR] 'node_modules' directory not found in %CD%
    echo [ACTION REQUIRED] Please install frontend dependencies: npm install or npm ci
    echo.
    pause
    exit /b 1
)

echo [INFO] Launching Vite development server on port 5173...
call npx vite --host 0.0.0.0 --port 5173

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Vite server terminated unexpectedly with exit code %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)

pause

@echo off
title SaleFox - All 9 Brand Backends
cd /d "%~dp0"

echo ========================================================
echo Starting All 9 SaleFox Scrapers and Automation Engines...
echo ========================================================

if exist "%~dp0.venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment Python: .venv\Scripts\python.exe
    set "PY_BIN=%~dp0.venv\Scripts\python.exe"
) else (
    echo [WARNING] .venv not found. Falling back to system Python...
    set "PY_BIN=python"
)

"%PY_BIN%" run_all_backends.py
pause

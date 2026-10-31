@echo off
setlocal

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Run: python -m venv .venv
    exit /b 1
)

if not exist ".env" (
    echo Configuration file .env not found.
    echo Run: copy .env.example .env
    echo Then set the PostgreSQL password in .env.
    exit /b 1
)

if "%~1"=="" (
    ".venv\Scripts\python.exe" run.py
) else (
    ".venv\Scripts\python.exe" run.py --port %~1
)

endlocal

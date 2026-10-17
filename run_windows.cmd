@echo off
setlocal

set "PORT=%~1"
if "%PORT%"=="" set "PORT=8010"

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

echo Starting Cloud Application at http://127.0.0.1:%PORT%
echo Swagger UI: http://127.0.0.1:%PORT%/docs
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port %PORT% --reload

endlocal

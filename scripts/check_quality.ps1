Write-Host "1. Ruff lint"

.\.venv\Scripts\python.exe -m ruff check app scripts

if ($LASTEXITCODE -ne 0) {
    Write-Error "Ruff lint failed"
    exit $LASTEXITCODE
}

Write-Host "2. Ruff format check"

.\.venv\Scripts\python.exe -m ruff format --check app scripts

if ($LASTEXITCODE -ne 0) {
    Write-Error "Ruff format check failed"
    exit $LASTEXITCODE
}

Write-Host "QUALITY CHECK PASSED"

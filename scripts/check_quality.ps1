$ErrorActionPreference = "Stop"
Write-Host "1. Ruff lint"
ruff check app scripts
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "2. Ruff format check"
ruff format --check app scripts
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "QUALITY CHECK PASSED"

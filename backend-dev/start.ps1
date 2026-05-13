# start.ps1 — Jalankan backend Test Flow Kit dengan konfigurasi yang benar
# Gunakan: .\start.ps1

$reloadExcludes = @(
    "engine-testing",
    "venv",
    "venv_310",
    "jacoco-engine",
    "__pycache__",
    "*.pyc"
)

$excludeArgs = $reloadExcludes | ForEach-Object { "--reload-exclude", $_ }

Write-Host "Starting Test Flow Kit Backend..." -ForegroundColor Cyan
Write-Host "URL: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""

& ".\venv\Scripts\python.exe" -m uvicorn main:app --reload @excludeArgs

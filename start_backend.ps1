# PowerShell script to start backend with GCP credentials
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Paper Brain ANN\gcp-key.json"

Write-Host "✅ GOOGLE_APPLICATION_CREDENTIALS set to: $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Green
Write-Host "Starting uvicorn server..." -ForegroundColor Cyan

uvicorn server:app --reload --port 8000


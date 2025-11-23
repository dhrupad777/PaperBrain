@echo off
REM Batch script to start backend with GCP credentials
set GOOGLE_APPLICATION_CREDENTIALS=C:\Paper Brain ANN\gcp-key.json

echo ✅ GOOGLE_APPLICATION_CREDENTIALS set to: %GOOGLE_APPLICATION_CREDENTIALS%
echo Starting uvicorn server...

uvicorn server:app --reload --port 8000


@echo off
echo ========================================
echo  GreenForge AI - Starting Backend
echo ========================================
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/api/docs
echo Press Ctrl+C to stop
echo.

:: Kill any process already using port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo Freeing port 8000 from PID %%a ...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

cd /d D:\1m1b\greenforge-ai\backend
D:\1m1b\greenforge-ai\backend\venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

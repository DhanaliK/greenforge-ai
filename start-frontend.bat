@echo off
echo ========================================
echo  GreenForge AI - Starting Frontend
echo ========================================
echo Frontend: http://localhost:3000
echo Press Ctrl+C to stop
echo.

:: Kill any process already using port 3000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000 " ^| findstr "LISTENING"') do (
    echo Freeing port 3000 from PID %%a ...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

set PATH=%PATH%;C:\Program Files\nodejs
cd /d D:\1m1b\greenforge-ai\frontend
npm run dev

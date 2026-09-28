@echo off
echo ========================================
echo  GreenForge AI — Running Tests
echo ========================================
cd /d D:\1m1b\greenforge-ai\backend
D:\1m1b\greenforge-ai\backend\venv\Scripts\python -m pytest tests/ -v
pause

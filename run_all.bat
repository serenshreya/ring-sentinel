@echo off
echo Starting Ring Sentinel full-stack system...
start "" D:\ring-sentinel\run_backend.bat
timeout /t 2 /nobreak >nul
start "" D:\ring-sentinel\run_frontend.bat
echo Both services launched!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173

@echo off
title Ring Sentinel - Backend (FastAPI)
echo ====================================================
echo Starting Ring Sentinel Backend on http://localhost:8000
echo ====================================================
cd /d D:\ring-sentinel\backend
D:\ring-sentinel\backend\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause

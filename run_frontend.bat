@echo off
title Ring Sentinel - Frontend (React + Vite)
echo ====================================================
echo Starting Ring Sentinel Frontend on http://localhost:5173
echo ====================================================
cd /d D:\ring-sentinel\frontend
set PATH=D:\ring-sentinel\tools\node-v20.18.0-win-x64;%PATH%
npm run dev
pause

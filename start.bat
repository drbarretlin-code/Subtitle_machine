@echo off
title AI Subtitle Machine Starter
echo 🚀 Starting AI Subtitle Machine...

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo 📦 Starting Backend Server...
start cmd /k "python server.py"

echo ⏳ Waiting for model initialization (5s)...
timeout /t 5 /nobreak > nul

echo 🎨 Starting Frontend Interface...
cd frontend
start cmd /k "npm run dev"

echo ✅ Startup commands sent.
echo 💡 Please open the URL shown in the frontend terminal (usually http://localhost:5173).
timeout /t 2 /nobreak > nul
start http://localhost:5173

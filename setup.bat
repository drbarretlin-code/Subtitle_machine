@echo off
title AI Subtitle Machine Setup
echo 🚀 Starting Environment Setup...

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo 🎨 Installing Frontend UI dependencies...
cd frontend
call npm install
cd ..

echo ✅ Setup Complete!
echo 💡 Next Step: Configure .env and run start.bat to launch.
pause

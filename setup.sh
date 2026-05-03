#!/bin/bash

# --- AI 字幕機 環境自動安裝腳本 ---

echo "🚀 開始安裝 AI 字幕機環境..."

# 1. 安裝 Python 依賴
echo "📦 正在安裝 Python 依賴套件..."
pip3 install -r requirements.txt

# 2. 安裝前端依賴
echo "🎨 正在安裝前端 UI 依賴套件..."
cd frontend && npm install && cd ..

echo "✅ 環境安裝完成！"
echo "💡 下一步：請配置 .env 檔案並執行 ./start.sh 啟動系統。"

#!/bin/bash

# --- AI 字幕機 自動啟動腳本 ---

# 1. 取得專案根目錄路徑
PROJECT_DIR="/Users/barretlin/Antigravity/Subtitle＿machine"
cd "$PROJECT_DIR"

echo "🚀 正在啟動 AI 字幕機..."

# 2. 啟動後端引擎 (開啟新分頁執行)
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && python3 server.py\""

echo "⏳ 等待後端引擎載入模型 (約 5 秒)..."
sleep 5

# 3. 啟動前端介面 (開啟新分頁執行)
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR/frontend' && npm run dev\""

echo "✅ 啟動程序已發送。請在瀏覽器中開啟終端機顯示的 URL。"
echo "💡 提示：預設網址通常為 http://localhost:5173"

# 4. 偵測區域網路 IP (便利行動裝置連線)
LOCAL_IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo "127.0.0.1")
echo "📱 行動裝置連線網址: http://$LOCAL_IP:5173"

# 5. 自動開啟網頁
sleep 2
open "http://localhost:5173"


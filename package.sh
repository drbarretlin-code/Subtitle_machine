#!/bin/bash

# --- AI 字幕機 專案打包腳本 ---
# 用途：自動剔除敏感資訊與冗餘檔案，生成乾淨的發布壓縮檔。

export ZIP_NAME="Subtitle_Machine_v1.0.zip"

echo "📦 正在準備打包專案..."

# 1. 建立臨時打包目錄
mkdir -p ./dist_tmp

# 2. 複製必要檔案 (排除敏感與巨大檔案)
# 排除：.env (金鑰), node_modules (前端依賴), __pycache__ (編譯暫存), .git (版本庫)
rsync -av --progress ./ ./dist_tmp \
    --exclude '.env' \
    --exclude '.git' \
    --exclude 'node_modules' \
    --exclude 'frontend/node_modules' \
    --exclude '__pycache__' \
    --exclude '.DS_Store' \
    --exclude 'dist_tmp' \
    --exclude "$ZIP_NAME"

# 3. 壓縮
cd ./dist_tmp
zip -r "../$ZIP_NAME" ./*

# 4. 清理
cd ..
rm -rf ./dist_tmp

echo "✅ 打包完成！"
echo "📄 檔案名稱：$ZIP_NAME"
echo "⚠️ 提醒：發送此壓縮檔給他人時，請提醒對方需自備 API 金鑰並填入 .env 檔案中。"

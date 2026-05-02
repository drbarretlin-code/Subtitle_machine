# AI 多語系即時字幕機 - 操作使用手冊 (2026 最終修訂版)

本手冊提供「AI 多語系即時字幕機」的完整操作流程、技術細節與故障排除指南。

---

## 1. 產品概覽
本系統是一款基於 `faster-whisper` 與 `Google Gemini 1.5 Flash` 的即時語音辨識與校正工具。
- **核心功能**: 即時語音轉文字 (ASR)、多國口音校正與翻譯 (LLM Translation)、即時字幕展示 (WebSocket UI)。
- **支援語系**: 繁中、英文、日文、韓文、泰文 (Thai)、菲律賓文 (Tagalog)、越南文 (Vietnamese) 等。
- **介面尺寸**: 固定 840 x 240 (適合水平滾動字幕)。

---

## 2. 環境與系統要求
- **作業系統**: macOS (推薦), Windows 10/11。
- **必備軟體**: 
  - Python 3.12+ (macOS 請使用 `python3`)
  - Node.js 18+
- **硬體建議**: 
  - 建議具備穩定網路連線以調用 Gemini API。
  - 模型預設為 `small` 精度模式，初次運行需下載約 500MB 模型。

---

## 3. 安裝與設定 (初次使用)

### 3.1 基礎環境初始化 (macOS)
1. **執行 SSL 憑證修復**:
   在終端機執行：`/Applications/Python\ 3.14/Install\ Certificates.command`
2. **安裝後端依賴**:
   ```bash
   cd /Users/barretlin/Antigravity/Subtitle＿machine
   pip3 install -r requirements.txt
   ```
3. **安裝前端依賴**:
   ```bash
   cd frontend && npm install && cd ..
   ```

### 3.2 API 金鑰設定
1. 在專案根目錄建立 `.env` 檔案。
2. 填入：`GOOGLE_API_KEYS=您的金鑰內容` (多組請用逗點隔開)。

---

## 4. 啟動流程 (自動化模式 - 推薦)

### macOS 一鍵啟動
1. 開啟終端機，進入專案目錄：
   ```bash
   cd /Users/barretlin/Antigravity/Subtitle＿machine
   ```
2. 執行啟動腳本：
   ```bash
   ./start.sh
   ```
3. 腳本將自動：
   - 開啟新視窗啟動 **AI 辨識引擎** (後端)。
   - 開啟新視窗啟動 **字幕展示介面** (前端)。
   - 自動開啟瀏覽器並跳轉至字幕視窗。

---

## 5. 使用操作指南
1. **選擇語系**: 
   - 左側選單選擇「輸入語系」(即您說話的語言)。
   - 右側選單選擇「目標語系」(即您希望字幕顯示的語言)。
2. **開始錄音**: 點擊介面右下方的「START」按鈕。
3. **字幕查看**: 字幕將由左至右平行滾動顯示。
4. **停止錄音**: 再次點擊按鈕即可停止。

---

## 6. 故障排除 (FAQ)

| 錯誤現象 | 可能原因 | 解決方法 |
| :--- | :--- | :--- |
| `zsh: command not found: python` | macOS 指令集差異 | 請使用 `python3` 或 `pip3` |
| `SSL: CERTIFICATE_VERIFY_FAILED` | macOS SSL 憑證未初始化 | 執行 `Install Certificates.command` |
| `ERROR: onnxruntime-gpu` | Mac 不支援 GPU 套件 | 已修正，請重新執行 `pip3 install -r requirements.txt` |
| 沒有字幕出現 | 瀏覽器錄音權限/WebSocket | 1. 允許瀏覽器麥克風。 2. 安裝 `websockets` 套件。 |

---

## 7. 維護與更新
- **更新專案**: 執行 `git pull`。
- **模型調校**: 可在 `server.py` 修改 `WHISPER_MODEL_SIZE` (若電腦卡頓可改回 `base`)。
- **安全性**: 嚴禁將 `.env` 檔案上傳至 GitHub。

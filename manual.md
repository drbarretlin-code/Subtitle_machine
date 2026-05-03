# 🌌 Antigravity AI 字幕機 (Subtitle Machine) 操作手冊

本手冊旨在引導使用者從零開始配置並運行 AI 字幕機。本系統採用最新的 **LPU (Language Processing Unit) 加速技術** 與 **混合式 AI 架構**，專為極速轉譯設計。

---

## 1. 核心設計邏輯 (How it works)

本系統不同於傳統字幕軟體，其設計核心在於「極速」與「精準」的完美平衡：

1.  **混合式辨識引擎 (Hybrid ASR)**：優先使用 **Groq Cloud (Whisper-large-v3)** 進行毫秒級語音轉文字；若雲端超額或斷線，系統會自動降級至 **本機 Whisper (Faster-Whisper)** 運作，確保服務不中斷。
2.  **雙階段即時更新 (Two-Phase Update)**：當您說話時，系統會先立即彈出「原始辨識文字」，隨後在 0.2 秒內由 **Llama 3 / Gemini** 完成「語境校正與翻譯」並原地覆蓋，實現零延遲感。
3.  **資源監測器**：介面內建即時配額監控，使用者可隨時掌握金鑰健康狀態與速率限制 (RPM)。

---

## 2. 系統要求與環境準備

### 適用作業系統
- **macOS (推薦)**: 支援最完美的透明視窗與音訊路由。
- **Windows 10/11**: 支援完整功能，建議使用 Chrome 瀏覽器。

### 必要軟體環境
1.  **Python 3.9+**: 負責處理後端辨識與翻譯邏輯。
2.  **Node.js 18+**: 負責執行前端字幕展示介面。
3.  **FFmpeg**: 處理音訊串流的關鍵工具。
4.  **音訊路由工具 (重要)**:
    - **macOS**: 必須安裝 [BlackHole (2ch)](https://existential.audio/blackhole/)，用以將系統音訊導入口語辨識引擎。
    - **Windows**: 使用系統預設的「立體聲混音 (Stereo Mix)」即可。

---

## 3. 零基礎安裝步驟

### Step 1: 取得金鑰 (API Keys)
本系統需要以下金鑰方可運作：
1.  **Groq API Key**: 前往 [Groq Console](https://console.groq.com/) 免費申請 (轉譯速度之魂)。
2.  **Google Gemini API Key**: 前往 [Google AI Studio](https://aistudio.google.com/) 申請 (高品質翻譯備援)。

### Step 2: 專案初始化
1.  解壓縮專案資料夾後，進入該目錄。
2.  **安裝 Python 依賴**:
    ```bash
    pip3 install -r requirements.txt
    ```
3.  **安裝前端依賴**:
    ```bash
    cd frontend && npm install && cd ..
    ```

### Step 3: 配置環境變數
在專案根目錄找到 `.env` 檔案（若無則新增），填入以下內容：
```env
# 格式：GOOGLE_API_KEYS=金鑰1,金鑰2 (支援多組輪替)
GOOGLE_API_KEYS=YOUR_GEMINI_KEY_HERE
GROQ_API_KEYS=YOUR_GROQ_KEY_HERE
```

---

## 4. 不同作業系統的音訊設定

### macOS (BlackHole 設定)
1.  開啟「音訊 MIDI 設定」應用程式。
2.  點擊左下角 `+`，建立「多重輸出裝置」。
3.  勾選「MacBook 揚聲器」與「BlackHole 2ch」。
4.  將系統「輸出裝置」設為此「多重輸出裝置」。
5.  在字幕機介面中，確保系統權限允許存取麥克風（實際上是抓取 BlackHole 的內容）。

### Windows (立體聲混音設定)
1.  右鍵點擊工作列音量圖示 ->「聲音」。
2.  在「錄製」分頁中，右鍵點擊空白處勾選「顯示停用的裝置」。
3.  啟用「立體聲混音 (Stereo Mix)」，並將其設為預設裝置。

---

## 5. 一鍵啟動指南 (Quick Start)

為了您的便利，我們將所有複雜指令打包成了自動化腳本。請根據您的系統，**直接複製並貼上**以下內容到您的終端機：

### 🍎 macOS 使用者
請複製以下整段指令並貼到終端機：
```bash
cd "/Users/barretlin/Antigravity/Subtitle＿machine" && chmod +x start.sh && ./start.sh
```

### 🪟 Windows 使用者
請開啟命令提示字元 (CMD) 並執行：
```cmd
cd /d "C:\您的路徑\Subtitle_machine" && start.bat
```

---

## 6. 系統限制與注意事項 (User Awareness)
- **免費金鑰限制**: Groq ASR 每分鐘限制約 20 次請求。若短時間內發話過於頻繁，監控燈號會變為紅色，系統將自動暫時切換為「本機辨識」。
- **網路延遲**: 翻譯速度取決於您與 API 伺服器的連線速度，建議在穩定的網路環境下使用。
- **雜訊過濾**: 系統已內建能量偵測，環境音太吵雜時會自動過濾，若發現不跳字幕，請確認說話音量。

---
**Antigravity 團隊製作 | 2026.05**

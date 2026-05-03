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
- **Python 3.9+** / **Node.js 18+** / **FFmpeg**
- **音訊路由工具**: macOS 需安裝 [BlackHole (2ch)](https://existential.audio/blackhole/)。

---

## 3. 零基礎「一鍵式」安裝步驟

### Step 1: 下載與安全性警告
1.  **取得程式碼**: 從 GitHub 下載 ZIP 並解壓縮。
2.  **⚠️ 重要安全性提示 (必讀)**:
    > [!CAUTION]
    > **自備環境與金鑰**: 本系統非單一執行檔，您**必須**安裝 Python/Node 環境。同時，請務必填寫您**個人的 API 金鑰**於 `.env` 中，嚴禁將包含金鑰的檔案傳給他人。

### Step 2: 一鍵安裝環境 (自動化)
請根據您的作業系統，複製以下指令並貼入終端機執行：

- **🍎 macOS 使用者**:
  ```bash
  cd "/Users/barretlin/Antigravity/Subtitle＿machine" && chmod +x setup.sh && ./setup.sh
  ```
- **🪟 Windows 使用者**:
  ```cmd
  cd /d "C:\您的路徑\Subtitle_machine" && setup.bat
  ```

---

## 4. 配置金鑰 (API Keys)

在專案目錄下找到 `.env` 檔案（若無則新增），填入您的金鑰：
```env
GOOGLE_API_KEYS=您的Gemini金鑰
GROQ_API_KEYS=您的Groq金鑰
```
*   **Groq 金鑰**: [Groq Console](https://console.groq.com/) (轉譯速度核心)。
*   **Gemini 金鑰**: [Google AI Studio](https://aistudio.google.com/) (品質校正備援)。

---

## 5. 一鍵啟動系統 (Quick Start)

安裝完成後，未來每次使用只需執行以下單一指令：

- **🍎 macOS 使用者**:
  ```bash
  cd "/Users/barretlin/Antigravity/Subtitle＿machine" && ./start.sh
  ```
- **🪟 Windows 使用者**:
  ```cmd
  cd /d "C:\您的路徑\Subtitle_machine" && start.bat
  ```

---

## 6. 開發者工具：一鍵打包發布 (For Developers)

若您需要將此專案「乾淨地」分享給他人，請執行以下指令。腳本會自動移除敏感金鑰與冗餘檔案，生成 `Subtitle_Machine_v1.0.zip`：

- **🍎 macOS 使用者**:
  ```bash
  cd "/Users/barretlin/Antigravity/Subtitle＿machine" && ./package.sh
  ```
- **🪟 Windows 使用者**: (請手動點擊目錄下的 `package.sh` 或使用 Git Bash 執行)

---

## 7. 系統限制與注意事項
- **免費限流**: 若發話過頻繁導致監控燈號變紅 (429)，系統將暫時切換為本機辨識。
- **雜訊過濾**: 內建能量偵測，若發現不跳字幕，請確認說話音量。

---

## 8. 行動裝置使用 (手機/平板)

本系統支援在同一個區域網路 (Wi-Fi) 下，使用手機或平板作為「遠端字幕顯示器」或「無線麥克風」。

### 操作步驟
1.  **取得電腦 IP**: 在電腦終端機輸入 `ifconfig` (macOS) 或 `ipconfig` (Windows)，找到您的區域網路 IP (例如 `192.168.1.100`)。
2.  **手機連線**: 確保手機與電腦連線至同一個 Wi-Fi。
3.  **開啟瀏覽器**: 在手機瀏覽器輸入 `http://電腦IP:5173`。
4.  **功能支援**:
    - **遠端觀看**: 您可以在平板上同步觀看電腦端產出的字幕，適合演講者查看。
    - **無線麥克風**: 在手機端點擊「START SESSION」，即可將手機當作無線麥克風進行辨識。
5.  **注意**: 行動裝置受限於系統安全性，無法直接抓取手機內部的系統音訊（如 Youtube App 聲音），僅支援麥克風收音。

### 8.1 遠端存取 (不在同一個 Wi-Fi 下)
若手機與電腦不在同一個網路環境，我們已完成「埠口合併 (Port Proxy)」，您只需穿透一個連接埠 (5173) 即可同時傳輸介面與語音數據。

#### 方案 A：使用 Ngrok (最穩定，推薦)
1.  註冊並下載 [Ngrok](https://ngrok.com/)。
2.  在終端機執行：`ngrok http 5173`。
3.  複製產出的 `https://xxxx.ngrok-free.app` 網址到手機開啟。

#### 方案 B：使用 Localtunnel (免註冊)
1.  執行 `npx localtunnel --port 5173`。
2.  **注意**: 第一次開啟網址時，會看到一個藍色的驗證頁面，請點擊「**Click to Continue**」或輸入終端機顯示的 IP 位址才能進入字幕機。

---
**Dr. Barret Lin 製作 | 2026.05**

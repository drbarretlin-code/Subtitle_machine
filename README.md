# AI 多語系即時字幕機 - 零基礎使用指南

本專案旨在提供一個極低延遲、具備口音校正功能的即時字幕解決方案。以下是為非開發人員準備的逐步設定教學。

---

## 第一步：準備環境 (工具安裝)

1. **安裝 Python**: 
   - 前往 [python.org](https://www.python.org/) 下載並安裝最新版本。
   - **重要**: 安裝時請務必勾選 「Add Python to PATH」。

2. **安裝 Node.js**: 
   - 前往 [nodejs.org](https://nodejs.org/) 下載並安裝 「LTS」 版本。

---

## 第二步：取得免費 API 金鑰 (Gemini)

1. 前往 [Google AI Studio](https://aistudio.google.com/)。
2. 點擊 「Get API key」。
3. 建立一個新的 API Key。
4. **設定金鑰**:
   - 在專案根目錄 (Subtitle_machine) 建立一個新檔案，命名為 `.env` (注意前面有個點)。
   - 在檔案內寫入以下內容 (將 `你的金鑰` 替換掉)：
     ```text
     GOOGLE_API_KEY=你的金鑰內容
     ```

---

## 第三步：安裝必要套件

開啟終端機 (Terminal / Command Prompt)，進入專案資料夾後執行：

1. **後端套件**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **前端套件**:
   ```bash
   cd frontend
   npm install
   ```

---

## 第四步：啟動系統 (推薦)

您可以直接使用我為您準備的一鍵啟動腳本：

```bash
./start.sh
```

這會自動開啟兩個終端機視窗並啟動所有服務，隨後自動開啟瀏覽器。

---

## 備用的手動啟動流程

如果您想手動啟動，請分別開啟兩個終端機視窗：

### 視窗 A (啟動後端引擎)
```bash
python3 server.py
```
*看到 「WebSocket 已連接」 或 「正在載入模型」 即代表成功。*

### 視窗 B (啟動前端介面)
```bash
cd frontend
npm run dev
```
*點擊終端機中出現的網址 (例如 http://localhost:5173) 即可開啟介面。*

---

## 常見問題與參數調整

如果您具備一些基礎，可以手動修改 `server.py` 中的參數：

- **WHISPER_MODEL_SIZE**: 
  - `base` (預設): 速度最快，適合一般電腦。
  - `large-v3`: 準確度最高，但需要較強的顯卡 (GPU)。
- **DEVICE**:
  - `cpu`: 如果您沒有 NVIDIA 顯卡。
  - `cuda`: 如果您有 NVIDIA 顯卡且已安裝 CUDA 驅動。

---

## 支援語系說明
本系統支援：泰文、印尼文、越南文、馬來文、日文、韓文、繁體中文、英文。
系統會自動偵測語系並透過 Gemini 進行口音優化校正。

# AI 多語系即時字幕機 - 操作使用手冊

本手冊提供「AI 多語系即時字幕機」的完整操作流程、技術細節與故障排除指南。

---

## 1. 產品概覽
本系統是一款基於 `faster-whisper` 與 `Google Gemini 1.5 Flash` 的即時語音辨識與校正工具。
- **核心功能**: 即時語音轉文字 (ASR)、多國口音校正 (LLM Refinement)、即時字幕展示 (WebSocket UI)。
- **支援語系**: 泰、印、越、馬、日、韓、繁中、英文等。

---

## 2. 環境與系統要求
- **作業系統**: macOS (Intel/Apple Silicon), Windows 10/11, Linux。
- **必備軟體**: 
  - Python 3.9+ (建議 3.12+)
  - Node.js 18+
- **硬體建議**: 
  - 記憶體: 8GB 以上。
  - 網路: 需要網路連線以呼叫 Gemini API。

---

## 3. 安裝與設定 (初次使用)

### 3.1 基礎環境初始化
1. **執行 SSL 憑證修復 (僅限 macOS)**:
   在終端機執行：`/Applications/Python\ 3.14/Install\ Certificates.command`
2. **安裝後端依賴**:
   ```bash
   pip3 install -r requirements.txt
   ```
3. **安裝前端依賴**:
   ```bash
   cd frontend && npm install && cd ..
   ```

### 3.2 API 金鑰設定
1. 在專案根目錄建立 `.env` 檔案。
2. 填入：`GOOGLE_API_KEY=您的金鑰`。

---

## 4. 每日啟動流程

### 步驟 A：啟動 AI 辨識引擎
開啟終端機，進入專案目錄執行：
```bash
python3 server.py
```
*提示：看到「正在載入模型」後，請等待直到不再出現新訊息。*

### 步驟 B：開啟使用者介面
開啟第二個終端機視窗，進入專案目錄執行：
```bash
cd frontend && npm run dev
```
*點擊出現的連結 (如 http://localhost:5173) 即可進入字幕視窗。*

---

## 5. 使用操作指南
1. **開始錄音**: 點擊介面下方的「開始監聽」按鈕。
2. **語音輸入**: 對著麥克風說話，系統會自動偵測停頓並進行辨識。
3. **字幕查看**: 
   - **灰色文字**: 原始辨識內容 (可能包含口音誤差)。
   - **白色文字**: 經 Gemini 校正後的流暢字幕。
4. **停止錄音**: 再次點擊按鈕即可停止。

---

## 6. 故障排除 (FAQ)

| 錯誤現象 | 可能原因 | 解決方法 |
| :--- | :--- | :--- |
| `command not found: python3` | 未安裝 Python 或未加入 PATH | 重新安裝 Python 並勾選 Add to PATH |
| `SSL: CERTIFICATE_VERIFY_FAILED` | macOS SSL 憑證未初始化 | 執行 `Install Certificates.command` |
| `ModuleNotFoundError` | 套件未完整安裝 | 重新執行 `pip3 install -r requirements.txt` |
| 字幕完全沒反應 | 瀏覽器錄音權限未開啟 | 點擊瀏覽器網址列左側鎖頭圖示，允許麥克風 |

---

## 7. 維護與更新
- **更新程式碼**: 執行 `git pull`。
- **更換模型**: 在 `server.py` 修改 `WHISPER_MODEL_SIZE` (base/small/medium/large-v3)。
- **清理快取**: 若模型下載錯誤，可刪除 `~/.cache/huggingface` 與 `~/.cache/torch`。

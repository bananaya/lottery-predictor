# 多樂透遊戲預測系統 v3.0

一個支援所有台灣彩券樂透遊戲的智能預測系統，運用先進演算法提供高信心度的號碼預測。

## 🎯 支援的樂透遊戲

### 主要樂透遊戲
- **大樂透** (Lotto 6/49) - 從1-49選6個號碼，特別號1-49
- **威力彩** (Power Ball) - 從1-38選6個號碼，特別號1-8
- **今彩539** (Daily Cash) - 從1-39選5個號碼
- **雙贏彩** (Double Win) - 從1-24選12個號碼

### 數字遊戲
- **3星彩** (Pick 3) - 3位數字遊戲，每位0-9
- **4星彩** (Pick 4) - 4位數字遊戲，每位0-9

### 特殊遊戲
- **BINGO BINGO** - 從1-80選20個號碼
- **38樂合彩** - 基於今彩539衍生，從1-38選5個號碼
- **49樂合彩** - 基於大樂透衍生，從1-49選6個號碼

## ✨ 主要功能

### 🧠 智能預測演算法
- **頻率分析**：基於歷史號碼出現頻率進行統計分析
- **模式識別**：識別號碼間的關聯模式和趨勢
- **混合演算法**：綜合多種方法的智能預測（推薦）
- **機器學習**：使用先進的ML模型進行預測

### 📊 Google Sheets 整合
- **自動資料儲存**：爬取的歷史資料自動儲存到指定的Google Sheets
- **預測結果記錄**：所有預測結果都會記錄到Google Sheets供追蹤
- **優先資料來源**：系統優先使用Google Sheets中的資料進行預測
- **多工作表支援**：不同樂透遊戲使用不同的工作表管理

### 🎚️ 信心度控制
- **可調整閾值**：50%-95%範圍內自由調整最低信心度要求
- **智能過濾**：只顯示達到信心度要求的預測結果
- **信心度指標**：每次預測都會顯示實際信心度百分比

### 🌐 現代化介面
- **響應式設計**：支援桌面和行動裝置
- **遊戲選擇器**：直觀的下拉選單選擇樂透遊戲
- **即時預覽**：遊戲資訊即時顯示
- **美觀的號碼球**：視覺化的號碼顯示效果

## 🚀 快速開始

### 環境需求
- Python 3.11+
- Flask 2.0+
- Google Sheets API 憑證

### 安裝步驟

1. **克隆專案**
```bash
git clone <your-repository-url>
cd lottery_predictor
```

2. **建立虛擬環境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安裝依賴**
```bash
pip install -r requirements.txt
```

4. **設定 Google Sheets API**
   - 前往 [Google Cloud Console](https://console.cloud.google.com/)
   - 建立新專案或選擇現有專案
   - 啟用 Google Sheets API
   - 建立服務帳戶並下載 JSON 金鑰檔案
   - 將金鑰檔案重新命名為 `google_service_account.json` 並放在專案根目錄

5. **設定環境變數**
```bash
export GOOGLE_SERVICE_ACCOUNT_KEY="$(cat google_service_account.json)"
```

6. **啟動應用程式**
```bash
python src/main.py
```

7. **開啟瀏覽器**
   訪問 `http://localhost:5000` 開始使用

## 📖 使用指南

### 基本操作流程

1. **選擇樂透遊戲**
   - 從下拉選單中選擇要預測的樂透遊戲
   - 系統會自動顯示該遊戲的規則資訊

2. **設定參數**
   - **Google Sheets 名稱**：輸入您的Google Sheets檔案名稱
   - **參考期數**：設定要參考的歷史期數（建議20-50期）
   - **預測方法**：選擇預測演算法
   - **最低信心度**：調整信心度閾值（建議70%以上）

3. **爬取歷史資料**
   - 點擊「爬取歷史資料」按鈕
   - 系統會自動從台灣彩券網站獲取最新資料
   - 資料會自動儲存到您的Google Sheets

4. **進行預測**
   - 點擊「預測下一期號碼」按鈕
   - 系統會分析歷史資料並產生預測結果
   - 只有達到信心度要求的預測才會顯示

### 進階功能

#### 多遊戲管理
- 系統支援同時管理多種樂透遊戲的資料
- 每種遊戲使用獨立的工作表儲存資料
- 預測結果會記錄遊戲類型和時間戳記

#### 衍生遊戲支援
- **38樂合彩**：基於今彩539的開獎號碼衍生
- **49樂合彩**：基於大樂透的開獎號碼衍生
- 系統會自動處理衍生關係並生成對應資料

## 🔧 API 文件

### 獲取支援的遊戲列表
```http
GET /api/games
```

### 爬取樂透資料
```http
POST /api/crawl
Content-Type: application/json

{
  "game_type": "lotto649",
  "periods": 20,
  "sheet_name": "樂透資料"
}
```

### 預測號碼
```http
POST /api/predict
Content-Type: application/json

{
  "game_type": "lotto649",
  "periods": 20,
  "sheet_name": "樂透資料",
  "method": "hybrid",
  "min_confidence": 0.7
}
```

### 獲取歷史資料
```http
POST /api/history
Content-Type: application/json

{
  "game_type": "lotto649",
  "periods": 20,
  "sheet_name": "樂透資料"
}
```

### 系統健康檢查
```http
GET /api/health
```

## 🏗️ 系統架構

### 核心模組
- **MultiLotteryCrawler**：多樂透遊戲爬蟲引擎
- **MultiLotteryGoogleSheetsManager**：Google Sheets 資料管理
- **MultiLotteryPredictionAlgorithm**：多遊戲預測演算法
- **Flask API**：RESTful API 服務

### 資料流程
1. 爬蟲模組從台灣彩券網站獲取開獎資料
2. 資料管理模組將資料儲存到Google Sheets
3. 預測模組從Google Sheets讀取資料進行分析
4. API模組提供統一的介面供前端呼叫

## 🚀 部署到 Render

### 準備工作
1. 將程式碼推送到 GitHub 儲存庫
2. 確保 `requirements.txt` 包含所有依賴
3. 準備 Google Sheets API 金鑰

### Render 部署步驟
1. 登入 [Render](https://render.com/)
2. 建立新的 Web Service
3. 連接您的 GitHub 儲存庫
4. 設定環境變數：
   - `GOOGLE_SERVICE_ACCOUNT_KEY`：Google Sheets API 金鑰內容
5. 設定建置命令：`pip install -r requirements.txt`
6. 設定啟動命令：`python src/main.py`
7. 點擊部署

### 環境變數設定
```bash
GOOGLE_SERVICE_ACCOUNT_KEY={"type":"service_account",...}
PORT=5000
```

## 🔍 故障排除

### 常見問題

#### Google Sheets 連線失敗
- 檢查服務帳戶金鑰是否正確設定
- 確認 Google Sheets API 已啟用
- 驗證工作表名稱是否存在

#### 爬蟲無法獲取資料
- 檢查網路連線
- 確認台灣彩券網站是否正常運作
- 檢查遊戲類型是否正確

#### 預測信心度不足
- 增加參考期數
- 降低最低信心度要求
- 嘗試不同的預測方法

#### 部署失敗
- 檢查 requirements.txt 是否完整
- 確認環境變數設定正確
- 查看部署日誌找出具體錯誤

## 📝 更新日誌

### v3.0 (2025-08-02)
- ✨ 新增支援9種樂透遊戲
- 🧠 實作多遊戲預測演算法
- 📊 完整的Google Sheets多工作表支援
- 🎨 全新的響應式使用者介面
- 🔧 RESTful API 重構
- 📱 行動裝置優化

### v2.0 (2025-08-01)
- ✨ 新增預測信心度閾值控制
- 📊 優先使用Google Sheets資料
- 🧠 改進預測演算法
- 🎨 美化使用者介面

### v1.0 (2025-07-31)
- 🎯 基礎大樂透預測功能
- 📊 Google Sheets整合
- 🌐 Web介面
- 🚀 Render部署支援

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request 來改善這個專案！

### 開發環境設定
1. Fork 這個專案
2. 建立功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 建立 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 檔案。

## ⚠️ 免責聲明

本系統僅供娛樂和學習用途。預測結果不保證準確性，請理性購買彩券，切勿沉迷賭博。

## 📞 聯絡資訊

如有任何問題或建議，請透過以下方式聯絡：
- GitHub Issues: [專案Issues頁面]
- Email: [您的聯絡信箱]

---

**祝您好運！🍀**


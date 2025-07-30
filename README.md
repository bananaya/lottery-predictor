# 大樂透號碼預測系統

這是一個使用 Python Flask 開發的大樂透號碼預測系統，具備以下功能：

## 主要功能

1. **歷史資料爬取**：從台灣彩券網站爬取大樂透歷史開獎資料
2. **Google Sheets 整合**：將資料自動儲存到 Google Sheets
3. **AI 預測演算法**：基於歷史資料進行號碼預測
4. **RESTful API**：提供完整的 API 介面
5. **網頁介面**：直觀的前端操作介面

## 技術架構

- **後端**：Python Flask
- **資料儲存**：Google Sheets API
- **前端**：HTML/CSS/JavaScript
- **部署**：Render 平台
- **版本控制**：GitHub

## API 端點

### 1. 爬取歷史資料
```
POST /api/lottery/crawl
```
**請求參數：**
```json
{
  "periods": 20,
  "sheet_name": "大樂透資料"
}
```

### 2. 預測號碼
```
POST /api/lottery/predict
```
**請求參數：**
```json
{
  "periods": 20,
  "sheet_name": "大樂透資料"
}
```

### 3. 取得歷史資料
```
GET /api/lottery/history?periods=20
```

### 4. 健康檢查
```
GET /api/lottery/health
```

## 安裝與設定

### 1. 克隆專案
```bash
git clone <repository-url>
cd lottery_predictor
```

### 2. 建立虛擬環境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. Google Sheets API 設定

#### 步驟 1：建立 Google Cloud 專案
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Sheets API

#### 步驟 2：建立服務帳戶
1. 在 Google Cloud Console 中，前往「IAM 和管理」→「服務帳戶」
2. 點擊「建立服務帳戶」
3. 填寫服務帳戶詳細資訊
4. 授予「編輯者」角色
5. 建立並下載 JSON 金鑰檔案

#### 步驟 3：設定環境變數
將下載的 JSON 金鑰內容設定為環境變數：

**本地開發：**
```bash
export GOOGLE_SERVICE_ACCOUNT_KEY='{"type": "service_account", ...}'
```

**Render 部署：**
在 Render 的環境變數設定中新增：
- 變數名稱：`GOOGLE_SERVICE_ACCOUNT_KEY`
- 變數值：完整的 JSON 金鑰內容

### 5. 執行應用程式
```bash
python src/main.py
```

應用程式將在 `http://localhost:5000` 啟動。

## 部署到 Render

### 1. 準備 GitHub 儲存庫
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. 在 Render 建立服務
1. 前往 [Render](https://render.com/)
2. 連接 GitHub 帳戶
3. 選擇儲存庫
4. 設定部署參數：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/main.py`
   - **Environment**: `Python 3`

### 3. 設定環境變數
在 Render 的環境變數設定中新增：
- `GOOGLE_SERVICE_ACCOUNT_KEY`：Google 服務帳戶 JSON 金鑰

## 使用說明

### 網頁介面操作
1. 開啟應用程式網址
2. 設定參考期數和 Google Sheets 名稱
3. 點擊「爬取歷史資料」獲取開獎資料
4. 點擊「預測號碼」進行 AI 預測
5. 查看預測結果和信心度

### API 使用範例

**爬取資料：**
```bash
curl -X POST http://localhost:5000/api/lottery/crawl \
  -H "Content-Type: application/json" \
  -d '{"periods": 20, "sheet_name": "大樂透資料"}'
```

**預測號碼：**
```bash
curl -X POST http://localhost:5000/api/lottery/predict \
  -H "Content-Type: application/json" \
  -d '{"periods": 20, "sheet_name": "大樂透資料"}'
```

## 資料結構

### Google Sheets 結構

**歷史開獎資料工作表：**
| 期數 | 開獎日期 | 號碼1 | 號碼2 | 號碼3 | 號碼4 | 號碼5 | 號碼6 | 特別號 |
|------|----------|-------|-------|-------|-------|-------|-------|--------|

**預測結果工作表：**
| 預測日期 | 號碼1 | 號碼2 | 號碼3 | 號碼4 | 號碼5 | 號碼6 | 特別號 | 信心度 |
|----------|-------|-------|-------|-------|-------|-------|--------|--------|

## 預測演算法

系統使用以下方法進行號碼預測：

1. **頻率分析**：統計各號碼在歷史資料中的出現頻率
2. **權重計算**：根據出現頻率計算號碼權重
3. **隨機性調整**：加入適當的隨機性避免過度擬合
4. **信心度評估**：基於歷史資料的一致性計算預測信心度

## 注意事項

1. **免責聲明**：本系統僅供娛樂和學習用途，不保證預測準確性
2. **理性投注**：請理性對待彩券投注，切勿過度投資
3. **資料來源**：歷史資料來源為台灣彩券官方網站
4. **隱私保護**：請妥善保管 Google 服務帳戶金鑰

## 故障排除

### 常見問題

**Q: Google Sheets API 認證失敗**
A: 檢查環境變數 `GOOGLE_SERVICE_ACCOUNT_KEY` 是否正確設定

**Q: 爬取資料失敗**
A: 檢查網路連線和台灣彩券網站是否正常

**Q: 預測結果不合理**
A: 增加參考期數或檢查歷史資料品質

## 開發團隊

本專案由 AI 助手協助開發，整合了現代 Web 技術和機器學習概念。

## 授權

本專案採用 MIT 授權條款。


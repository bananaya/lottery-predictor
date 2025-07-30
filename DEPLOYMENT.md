# 部署指南

## 部署到 Render

### 1. 準備 GitHub 儲存庫

首先，將專案推送到 GitHub：

```bash
# 如果還沒有遠端儲存庫，先在 GitHub 建立一個新的儲存庫
git remote add origin https://github.com/YOUR_USERNAME/lottery-predictor.git
git branch -M main
git push -u origin main
```

### 2. 在 Render 建立 Web Service

1. 前往 [Render Dashboard](https://dashboard.render.com/)
2. 點擊 "New +" → "Web Service"
3. 連接您的 GitHub 帳戶並選擇 lottery-predictor 儲存庫
4. 設定以下參數：

**基本設定：**
- **Name**: `lottery-predictor`
- **Environment**: `Python 3`
- **Region**: 選擇最近的區域
- **Branch**: `main`

**Build & Deploy 設定：**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python src/main.py`

### 3. 設定環境變數

在 Render 的 Environment 設定中新增以下環境變數：

#### 必要環境變數：

**GOOGLE_SERVICE_ACCOUNT_KEY**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
}
```

### 4. Google Sheets API 設定

#### 步驟 1：建立 Google Cloud 專案
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Sheets API：
   - 前往 "APIs & Services" → "Library"
   - 搜尋 "Google Sheets API"
   - 點擊啟用

#### 步驟 2：建立服務帳戶
1. 前往 "IAM & Admin" → "Service Accounts"
2. 點擊 "Create Service Account"
3. 填寫服務帳戶詳細資訊：
   - **Service account name**: `lottery-predictor-service`
   - **Description**: `Service account for lottery predictor app`
4. 授予角色：
   - 選擇 "Editor" 角色
5. 建立金鑰：
   - 點擊建立的服務帳戶
   - 前往 "Keys" 標籤
   - 點擊 "Add Key" → "Create new key"
   - 選擇 JSON 格式
   - 下載金鑰檔案

#### 步驟 3：設定 Google Sheets 權限
1. 開啟您要使用的 Google Sheets
2. 點擊右上角的 "Share" 按鈕
3. 新增服務帳戶的 email（從 JSON 金鑰中的 client_email）
4. 授予 "Editor" 權限

### 5. 部署流程

1. **推送程式碼到 GitHub**：
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **在 Render 中部署**：
   - Render 會自動偵測到新的 commit
   - 開始建置和部署流程
   - 等待部署完成（通常需要 5-10 分鐘）

3. **檢查部署狀態**：
   - 在 Render Dashboard 中查看建置日誌
   - 確認沒有錯誤訊息
   - 測試應用程式 URL

### 6. 測試部署

部署完成後，您會獲得一個 Render URL，例如：
`https://lottery-predictor.onrender.com`

測試以下功能：
1. 開啟網站首頁
2. 測試系統健康檢查
3. 測試查看歷史資料
4. 測試預測功能
5. 檢查 Google Sheets 是否正確儲存資料

### 7. 常見問題排除

#### 問題 1：Google Sheets API 認證失敗
**解決方案**：
- 檢查環境變數 `GOOGLE_SERVICE_ACCOUNT_KEY` 是否正確設定
- 確認 JSON 格式正確（沒有多餘的空格或換行）
- 驗證服務帳戶是否有 Google Sheets 的存取權限

#### 問題 2：應用程式無法啟動
**解決方案**：
- 檢查 Render 的建置日誌
- 確認 `requirements.txt` 包含所有必要的依賴
- 檢查 Python 版本相容性

#### 問題 3：CORS 錯誤
**解決方案**：
- 確認已安裝並設定 `flask-cors`
- 檢查 CORS 設定是否正確

### 8. 更新部署

要更新已部署的應用程式：

1. 修改程式碼
2. 提交變更：
   ```bash
   git add .
   git commit -m "Update: 描述您的變更"
   git push origin main
   ```
3. Render 會自動重新部署

### 9. 監控和維護

- 定期檢查 Render 的日誌
- 監控應用程式效能
- 定期更新依賴套件
- 備份重要的 Google Sheets 資料

### 10. 成本考量

Render 免費方案限制：
- 每月 750 小時的運行時間
- 應用程式在閒置 15 分鐘後會進入睡眠狀態
- 第一次請求可能需要較長時間啟動

如需更好的效能，可考慮升級到付費方案。


# Render 部署故障排除指南

## 常見問題與解決方案

### 1. SQLite 資料庫錯誤

**錯誤訊息**：
```
sqlite3.OperationalError: unable to open database file
```

**原因**：
- Render 的免費層級不允許應用程式寫入檔案系統
- SQLite 需要在本地檔案系統建立資料庫檔案

**解決方案**：
已在 `src/main.py` 中註釋掉 SQLite 相關程式碼：
```python
# app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db.init_app(app)
# with app.app_context():
#     db.create_all()
```

### 2. 環境變數設定

**必要環境變數**：
- `GOOGLE_SERVICE_ACCOUNT_KEY`：Google Sheets API 金鑰（JSON 格式）

**設定方式**：
1. 在 Render Dashboard 中選擇您的服務
2. 前往 "Environment" 標籤
3. 新增環境變數

### 3. 建置命令設定

**正確的建置設定**：
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python src/main.py`

### 4. Python 版本相容性

如果遇到 Python 版本問題，可以在專案根目錄建立 `runtime.txt`：
```
python-3.11.0
```

### 5. 依賴套件問題

確認 `requirements.txt` 包含所有必要套件：
```
Flask==3.1.1
flask-cors==6.0.0
gspread==6.2.1
google-auth==2.40.3
beautifulsoup4==4.13.4
requests==2.32.4
numpy==2.3.2
```

### 6. 部署流程

1. **推送程式碼到 GitHub**：
   ```bash
   git add .
   git commit -m "Fix deployment issues"
   git push origin main
   ```

2. **在 Render 中重新部署**：
   - 前往 Render Dashboard
   - 選擇您的服務
   - 點擊 "Manual Deploy" → "Deploy latest commit"

3. **檢查部署日誌**：
   - 在 Render Dashboard 中查看 "Logs" 標籤
   - 確認沒有錯誤訊息

### 7. 測試部署

部署成功後，測試以下端點：
- `GET /api/lottery/health` - 健康檢查
- `GET /` - 主頁面

### 8. 常見錯誤排除

**錯誤：ModuleNotFoundError**
- 檢查 `requirements.txt` 是否包含所有依賴
- 確認建置命令正確

**錯誤：Port binding**
- 確認應用程式使用 `PORT` 環境變數
- 檢查 `app.run(host='0.0.0.0', port=port)`

**錯誤：CORS 問題**
- 確認已安裝並設定 `flask-cors`
- 檢查 `CORS(app)` 是否正確設定

### 9. 聯繫支援

如果問題持續存在：
1. 檢查 Render 的狀態頁面
2. 查看 Render 社群論壇
3. 聯繫 Render 支援團隊

### 10. 備用方案

如果 Render 部署持續失敗，可考慮：
- Heroku
- Railway
- Vercel（僅限靜態網站）
- PythonAnywhere


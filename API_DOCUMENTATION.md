# API 文件

## 基本資訊

- **Base URL**: `https://your-app.onrender.com/api/lottery`
- **Content-Type**: `application/json`
- **所有端點都支援 CORS**

## API 端點

### 1. 健康檢查

檢查系統是否正常運行。

**端點**: `GET /health`

**回應範例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-30 03:00:55"
}
```

---

### 2. 爬取歷史資料

從台灣彩券網站爬取大樂透歷史開獎資料並儲存到 Google Sheets。

**端點**: `POST /crawl`

**請求參數**:
```json
{
  "periods": 20,
  "sheet_name": "大樂透資料"
}
```

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| periods | integer | 是 | 要爬取的期數 (5-100) |
| sheet_name | string | 是 | Google Sheets 試算表名稱 |

**成功回應**:
```json
{
  "message": "成功爬取並儲存 20 期資料",
  "data": [
    {
      "period": "11400001",
      "date": "2025-07-28",
      "numbers": [5, 12, 28, 35, 42, 45],
      "special_number": 30,
      "game_type": "大樂透"
    }
  ]
}
```

**錯誤回應**:
```json
{
  "error": "無法爬取資料"
}
```

---

### 3. 預測號碼

基於歷史資料預測下一期大樂透號碼。

**端點**: `POST /predict`

**請求參數**:
```json
{
  "periods": 20,
  "sheet_name": "大樂透資料",
  "method": "hybrid"
}
```

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| periods | integer | 是 | 參考的歷史期數 (5-100) |
| sheet_name | string | 是 | Google Sheets 試算表名稱 |
| method | string | 否 | 預測方法 (frequency/pattern/hybrid/ml) |

**預測方法說明**:
- `frequency`: 基於號碼出現頻率
- `pattern`: 基於歷史模式分析
- `hybrid`: 混合多種方法 (預設)
- `ml`: 機器學習方法

**成功回應**:
```json
{
  "message": "預測完成",
  "prediction": {
    "predicted_numbers": [1, 13, 20, 24, 29, 34],
    "predicted_special": 49,
    "method": "hybrid",
    "confidence": 0.863,
    "prediction_date": "2025-07-30 03:01:37"
  },
  "historical_data_count": 20,
  "saved_to_sheets": true,
  "method_used": "hybrid"
}
```

**錯誤回應**:
```json
{
  "error": "無法取得歷史資料"
}
```

---

### 4. 取得歷史資料

取得指定期數的歷史開獎資料。

**端點**: `GET /history`

**查詢參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| periods | integer | 否 | 要取得的期數，預設 10 |

**範例**: `GET /history?periods=5`

**成功回應**:
```json
{
  "message": "取得 5 期歷史資料",
  "data": [
    {
      "period": "11400001",
      "date": "2025-07-28",
      "numbers": [5, 12, 28, 35, 42, 45],
      "special_number": 30,
      "game_type": "大樂透"
    }
  ]
}
```

---

## 錯誤代碼

| HTTP 狀態碼 | 說明 |
|-------------|------|
| 200 | 請求成功 |
| 400 | 請求參數錯誤 |
| 500 | 伺服器內部錯誤 |

## 使用範例

### cURL 範例

**健康檢查**:
```bash
curl -X GET https://your-app.onrender.com/api/lottery/health
```

**爬取資料**:
```bash
curl -X POST https://your-app.onrender.com/api/lottery/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "periods": 10,
    "sheet_name": "我的大樂透資料"
  }'
```

**預測號碼**:
```bash
curl -X POST https://your-app.onrender.com/api/lottery/predict \
  -H "Content-Type: application/json" \
  -d '{
    "periods": 20,
    "sheet_name": "我的大樂透資料",
    "method": "hybrid"
  }'
```

### JavaScript 範例

```javascript
// 預測號碼
async function predictNumbers() {
  try {
    const response = await fetch('/api/lottery/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        periods: 20,
        sheet_name: '大樂透資料',
        method: 'hybrid'
      })
    });
    
    const data = await response.json();
    console.log('預測結果:', data.prediction);
  } catch (error) {
    console.error('預測失敗:', error);
  }
}
```

### Python 範例

```python
import requests

# API 基本 URL
BASE_URL = "https://your-app.onrender.com/api/lottery"

def predict_lottery_numbers(periods=20, sheet_name="大樂透資料"):
    """預測大樂透號碼"""
    url = f"{BASE_URL}/predict"
    data = {
        "periods": periods,
        "sheet_name": sheet_name,
        "method": "hybrid"
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        prediction = result['prediction']
        print(f"預測號碼: {prediction['predicted_numbers']}")
        print(f"特別號: {prediction['predicted_special']}")
        print(f"信心度: {prediction['confidence']:.1%}")
    else:
        print(f"預測失敗: {response.json().get('error', '未知錯誤')}")

# 使用範例
predict_lottery_numbers()
```

## 注意事項

1. **Google Sheets 設定**: 使用前請確保已正確設定 Google Sheets API 認證
2. **速率限制**: 建議不要過於頻繁地呼叫 API，避免對台灣彩券網站造成負擔
3. **資料準確性**: 本系統僅供娛樂和學習用途，不保證預測準確性
4. **環境變數**: 部署時請確保設定正確的環境變數


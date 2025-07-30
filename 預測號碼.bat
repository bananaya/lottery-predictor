curl -X POST https://lotto-api-wslg.onrender.com/api/lottery/predict \
  -H "Content-Type: application/json" \
  -d '{
    "periods": 20,
    "sheet_name": "我的大樂透資料",
    "method": "hybrid"
  }'
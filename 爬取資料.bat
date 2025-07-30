curl -X POST https://lotto-api-wslg.onrender.com/api/lottery/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "periods": 10,
    "sheet_name": "我的大樂透資料"
  }'
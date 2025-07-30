from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
import sys

# 添加 utils 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from taiwan_lottery_crawler import TaiwanLotteryCrawler
from prediction_algorithm import LotteryPredictor

lottery_bp = Blueprint('lottery', __name__)

# Google Sheets 設定
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_google_sheets_client():
    """取得 Google Sheets 客戶端"""
    try:
        # 從環境變數讀取服務帳戶金鑰
        service_account_info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY', '{}'))
        credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        print(f"Google Sheets 認證失敗: {e}")
        return None

def crawl_lottery_data(periods=10):
    """爬取大樂透歷史資料"""
    try:
        crawler = TaiwanLotteryCrawler()
        lottery_data = crawler.get_lotto649_data(periods)
        return lottery_data
    except Exception as e:
        print(f"爬取資料失敗: {e}")
        return []

def predict_numbers(historical_data, method='hybrid'):
    """預測下一期大樂透號碼"""
    try:
        predictor = LotteryPredictor()
        prediction = predictor.predict_numbers(historical_data, method)
        return prediction
    except Exception as e:
        print(f"預測失敗: {e}")
        return None

def save_to_google_sheets(data, sheet_name, worksheet_name):
    """儲存資料到 Google Sheets"""
    try:
        client = get_google_sheets_client()
        if not client:
            return False
        
        # 開啟或建立試算表
        try:
            sheet = client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            sheet = client.create(sheet_name)
        
        # 開啟或建立工作表
        try:
            worksheet = sheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
        
        # 如果是歷史資料
        if isinstance(data, list) and len(data) > 0 and 'period' in data[0]:
            # 設定標題行
            headers = ['期數', '開獎日期', '號碼1', '號碼2', '號碼3', '號碼4', '號碼5', '號碼6', '特別號']
            worksheet.clear()
            worksheet.append_row(headers)
            
            # 新增資料
            for item in data:
                row = [
                    item['period'],
                    item['date'],
                    *item['numbers'],
                    item['special_number']
                ]
                worksheet.append_row(row)
        
        # 如果是預測資料
        elif isinstance(data, dict) and 'predicted_numbers' in data:
            # 設定標題行（如果工作表是空的）
            if worksheet.row_count == 0 or not worksheet.row_values(1):
                headers = ['預測日期', '號碼1', '號碼2', '號碼3', '號碼4', '號碼5', '號碼6', '特別號', '信心度']
                worksheet.clear()
                worksheet.append_row(headers)
            
            # 新增預測資料
            row = [
                data['prediction_date'],
                *data['predicted_numbers'],
                data['predicted_special'],
                data['confidence']
            ]
            worksheet.append_row(row)
        
        return True
    except Exception as e:
        print(f"儲存到 Google Sheets 失敗: {e}")
        return False

@lottery_bp.route('/crawl', methods=['POST'])
@cross_origin()
def crawl_lottery():
    """爬取大樂透資料並儲存到 Google Sheets"""
    try:
        data = request.get_json()
        periods = data.get('periods', 10)
        sheet_name = data.get('sheet_name', '大樂透資料')
        
        # 爬取資料
        lottery_data = crawl_lottery_data(periods)
        
        if not lottery_data:
            return jsonify({"error": "無法爬取資料"}), 500
        
        # 儲存到 Google Sheets
        success = save_to_google_sheets(lottery_data, sheet_name, '歷史開獎資料')
        
        if success:
            return jsonify({
                "message": f"成功爬取並儲存 {len(lottery_data)} 期資料",
                "data": lottery_data
            })
        else:
            return jsonify({
                "message": f"爬取成功但儲存失敗，共 {len(lottery_data)} 期資料",
                "data": lottery_data
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lottery_bp.route('/predict', methods=['POST'])
@cross_origin()
def predict_lottery():
    """預測下一期大樂透號碼"""
    try:
        data = request.get_json()
        periods = data.get('periods', 10)
        sheet_name = data.get('sheet_name', '大樂透資料')
        method = data.get('method', 'hybrid')  # 新增預測方法參數
        
        # 先爬取歷史資料
        historical_data = crawl_lottery_data(periods)
        
        if not historical_data:
            return jsonify({"error": "無法取得歷史資料"}), 500
        
        # 進行預測
        prediction = predict_numbers(historical_data, method)
        
        if not prediction:
            return jsonify({"error": "預測失敗"}), 500
        
        # 儲存預測結果到 Google Sheets
        save_success = save_to_google_sheets(prediction, sheet_name, '預測結果')
        
        return jsonify({
            "message": "預測完成",
            "prediction": prediction,
            "historical_data_count": len(historical_data),
            "saved_to_sheets": save_success,
            "method_used": method
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lottery_bp.route('/history', methods=['GET'])
@cross_origin()
def get_history():
    """取得歷史資料"""
    try:
        periods = request.args.get('periods', 10, type=int)
        historical_data = crawl_lottery_data(periods)
        
        return jsonify({
            "message": f"取得 {len(historical_data)} 期歷史資料",
            "data": historical_data
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lottery_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


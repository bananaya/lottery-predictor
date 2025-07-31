from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import json
from datetime import datetime
import os
import sys

# 添加 utils 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from taiwan_lottery_crawler import TaiwanLotteryCrawler
from prediction_algorithm import LotteryPredictor
from google_sheets_manager import GoogleSheetsManager

lottery_bp = Blueprint('lottery', __name__)

# Google Sheets 設定
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_google_sheets_manager():
    """取得 Google Sheets 管理器"""
    try:
        manager = GoogleSheetsManager()
        return manager
    except Exception as e:
        print(f"Google Sheets 管理器初始化失敗: {e}")
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

def predict_numbers_from_sheets(sheet_name, periods=20, method='hybrid', min_confidence=0.7):
    """從 Google Sheets 讀取資料並進行預測"""
    try:
        # 取得 Google Sheets 管理器
        sheets_manager = get_google_sheets_manager()
        if not sheets_manager:
            return None
        
        # 從 Google Sheets 讀取歷史資料
        historical_data = sheets_manager.read_historical_data(sheet_name)
        
        if not historical_data:
            print("Google Sheets 中沒有歷史資料，嘗試爬取新資料")
            # 如果沒有資料，先爬取一些資料
            crawled_data = crawl_lottery_data(periods)
            if crawled_data:
                sheets_manager.save_historical_data(sheet_name, crawled_data)
                historical_data = crawled_data
            else:
                return None
        
        # 限制使用的期數
        if len(historical_data) > periods:
            historical_data = historical_data[-periods:]
        
        # 進行預測
        predictor = LotteryPredictor()
        prediction = predictor.predict_numbers(historical_data, method)
        
        if prediction and prediction.get('confidence', 0) >= min_confidence:
            # 儲存預測結果到 Google Sheets
            sheets_manager.save_prediction_result(sheet_name, prediction)
            return prediction
        else:
            print(f"預測信心度 {prediction.get('confidence', 0):.3f} 低於最低要求 {min_confidence}")
            return None
            
    except Exception as e:
        print(f"從 Google Sheets 預測失敗: {e}")
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
    """爬取大樂透歷史資料並儲存到 Google Sheets"""
    try:
        data = request.get_json()
        periods = data.get('periods', 10)
        sheet_name = data.get('sheet_name', '大樂透資料')
        
        # 爬取歷史資料
        historical_data = crawl_lottery_data(periods)
        
        if not historical_data:
            return jsonify({"error": "無法爬取歷史資料"}), 500
        
        # 儲存到 Google Sheets
        sheets_manager = get_google_sheets_manager()
        if sheets_manager:
            save_success = sheets_manager.save_historical_data(sheet_name, historical_data)
        else:
            save_success = False
        
        return jsonify({
            "message": f"成功爬取並儲存 {len(historical_data)} 期資料",
            "data": historical_data,
            "saved_to_sheets": save_success
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500ry_data)} 期資料",
                "data": lottery_data
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lottery_bp.route('/predict', methods=['POST'])
@cross_origin()
def predict_lottery():
    """預測下一期大樂透號碼（使用 Google Sheets 資料和信心度閾值）"""
    try:
        data = request.get_json()
        periods = data.get('periods', 20)
        sheet_name = data.get('sheet_name', '大樂透資料')
        method = data.get('method', 'hybrid')
        min_confidence = data.get('min_confidence', 0.7)  # 預設最低信心度 70%
        
        # 從 Google Sheets 進行預測
        prediction = predict_numbers_from_sheets(sheet_name, periods, method, min_confidence)
        
        if not prediction:
            return jsonify({
                "error": f"預測失敗或信心度低於 {min_confidence:.1%}",
                "message": "請嘗試增加參考期數或降低信心度要求"
            }), 400
        
        # 取得歷史資料數量
        sheets_manager = get_google_sheets_manager()
        historical_data = []
        if sheets_manager:
            historical_data = sheets_manager.read_historical_data(sheet_name)
        
        return jsonify({
            "message": "預測完成",
            "prediction": prediction,
            "historical_data_count": len(historical_data),
            "method_used": method,
            "min_confidence_required": min_confidence,
            "actual_confidence": prediction.get@lottery_bp.route('/history', methods=['GET'])
@cross_origin()
def get_history():
    """取得歷史開獎資料（從 Google Sheets）"""
    try:
        periods = request.args.get('periods', 10, type=int)
        sheet_name = request.args.get('sheet_name', '大樂透資料')
        
        # 從 Google Sheets 取得歷史資料
        sheets_manager = get_google_sheets_manager()
        if not sheets_manager:
            return jsonify({"error": "Google Sheets 連接失敗"}), 500
        
        historical_data = sheets_manager.read_historical_data(sheet_name)
        
        if not historical_data:
            return jsonify({
                "message": "沒有找到歷史資料",
                "data": [],
                "suggestion": "請先使用爬取功能獲取歷史資料"
            })
        
        # 限制回傳的期數
        if len(historical_data) > periods:
            historical_data = historical_data[-periods:]
        
        return jsonify({
            "message": f"取得 {len(historical_data)} 期歷史資料",
            "data": historical_data
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500lottery_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


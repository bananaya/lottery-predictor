from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import json
from datetime import datetime
import os
import sys
import logging

# 添加 utils 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

# 設定 logging 格式
logging.basicConfig(
    format="[%(asctime)s][%(name)-5s][%(levelname)-5s] %(message)s (%(filename)s:%(lineno)d)",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from taiwan_lottery_crawler import TaiwanLotteryCrawlerClass
from prediction_algorithm import LotteryPredictor
from google_sheets_manager import GoogleSheetsManager

lottery_bp = Blueprint('lottery', __name__)

def get_google_sheets_manager():
    """取得 Google Sheets 管理器"""
    try:
        manager = GoogleSheetsManager()
        return manager
    except Exception as e:
        logging.critical(f"Google Sheets 管理器初始化失敗: {e}")
        return None

def crawl_lottery_data(periods=10):
    """爬取大樂透歷史資料"""
    try:
        crawler = TaiwanLotteryCrawlerClass()
        lottery_data = crawler.get_lotto_data("lotto649", crawler.extract_lotto649, periods)
        return lottery_data
    except Exception as e:
        logging.error(f"爬取資料失敗: {e}")
        return []

# def predict_numbers_from_sheets(sheet_name, periods=20, method='hybrid', min_confidence=0.7):
    # """從 Google Sheets 讀取資料並進行預測"""
    # try:
        # # 取得 Google Sheets 管理器
        # sheets_manager = get_google_sheets_manager()
        # if not sheets_manager:
            # return None
        
        # # 從 Google Sheets 讀取歷史資料
        # historical_data = sheets_manager.read_historical_data(sheet_name)
        
        # if not historical_data:
            # logging.info("Google Sheets 中沒有歷史資料，嘗試爬取新資料")
            # # 如果沒有資料，先爬取一些資料
            # crawled_data = crawl_lottery_data(periods)
            # if crawled_data:
                # sheets_manager.save_historical_data(sheet_name, crawled_data)
                # historical_data = crawled_data
            # else:
                # return None
        
        # # 限制使用的期數
        # if len(historical_data) > periods:
            # historical_data = historical_data[-periods:]
        
        # # 進行預測
        # predictor = LotteryPredictor()    
        # counter = 0
        # highestConfidence = 0
        # while True:
            # prediction = predictor.predict_numbers(historical_data, method)
            
            # counter = counter + 1 
            # if highestConfidence < prediction.get('confidence', 0):
                # highestConfidence = prediction.get('confidence', 0)
            # if prediction and prediction.get('confidence', 0) >= min_confidence:
                # logging.info(f"總共預測 {counter} 次產生號碼。")
                # break
            # if counter > 2000:
                # logging.warning(f"預測 {counter} 後沒有產生號碼。")
                # break
        
        # if prediction and prediction.get('confidence', 0) >= min_confidence:
            # # 儲存預測結果到 Google Sheets
            # sheets_manager.save_prediction_result(sheet_name, prediction)
            # return prediction
        # else:
            # logging.warning(f"預測信心度最高為 {highestConfidence:.3f} 低於最低要求 {min_confidence}")
            # return None
            
    # except Exception as e:
        # logging.error(f"從 Google Sheets 預測失敗: {e}")
        # return None
        
def predict_numbers_from_sheets(sheet_name, periods=20, method='hybrid', min_confidence=0.7, total_predictions=5):
    """從 Google Sheets 讀取資料並進行預測"""
    from collections import Counter
    
    try:
        # 取得 Google Sheets 管理器
        sheets_manager = get_google_sheets_manager()
        if not sheets_manager:
            return None
        
        # 從 Google Sheets 讀取歷史資料
        historical_data = sheets_manager.read_historical_data(sheet_name)
        
        if not historical_data:
            logging.info("Google Sheets 中沒有歷史資料，嘗試爬取新資料")
            # 如果沒有資料，先爬取一些資料
            crawled_data = crawl_lottery_data(periods)
            if crawled_data:
                sheets_manager.save_historical_data(sheet_name, crawled_data)
                historical_data = crawled_data
            else:
                return None, []
        
        # 限制使用的期數
        if len(historical_data) > periods:
            historical_data = historical_data[-periods:]
        
        # 進行預測
        predictor = LotteryPredictor()    
        predictions = []        
        max_attempts = 500
        counter = 0
        
        while len(predictions) < total_predictions:
            attempts = 0
            highestConfidence = 0
            while attempts < max_attempts:
                attempts += 1
                prediction = predictor.predict_numbers(historical_data, method)
                if highestConfidence < prediction.get('confidence', 0):
                    highestConfidence = prediction.get('confidence', 0)
                if prediction and prediction.get('confidence', 0) >= min_confidence:
                    predictions.append(prediction)
                    break
            
            if attempts == max_attempts:
                logging.warning(f"第 {len(predictions)+1} 預測，信心度最高為 {highestConfidence:.3f} 低於最低要求 {min_confidence}")
                return None, []
            
        # 統計號碼出現次數
        main_number_counter = Counter()
        special_number_counter = Counter()

        for pred in predictions:
            main_number_counter.update(pred.get("predicted_numbers", []))
            special = pred.get("predicted_special")
            if special is not None:
                special_number_counter[special] += 1

        # 最常出現的 6 個主號
        best_main_numbers = [num for num, _ in main_number_counter.most_common(6)]
        best_special = special_number_counter.most_common(1)[0][0] if special_number_counter else None
        
        # 建立最佳預測組合
        best_prediction = {
            "prediction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "predicted_numbers": sorted(best_main_numbers),
            "predicted_special": best_special,
            "confidence": min_confidence,
            "method": f"{method}_top-frequency-from-{total_predictions}-predictions",
        }   
        sheets_manager.save_prediction_result(sheet_name, best_prediction)
        
        logging.info(f"成功從 {total_predictions} 組預測中統計出最佳號碼")
        return best_prediction, predictions

    except Exception as e:
        logging.error(f"預測過程發生錯誤: {e}")
        return None, []

@lottery_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

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
        return jsonify({"error": str(e)}), 500

@lottery_bp.route('/predict', methods=['POST'])
@cross_origin()
# def predict_lottery():
    # """預測下一期大樂透號碼（使用 Google Sheets 資料和信心度閾值）"""
    # try:
        # data = request.get_json()
        # periods = data.get('periods', 20)
        # sheet_name = data.get('sheet_name', '大樂透資料')
        # method = data.get('method', 'hybrid')
        # min_confidence = data.get('min_confidence', 0.7)  # 預設最低信心度 70%
        
        # # 從 Google Sheets 進行預測
        # prediction = predict_numbers_from_sheets(sheet_name, periods, method, min_confidence)
        
        # if not prediction:
            # return jsonify({
                # "error": f"預測失敗或信心度低於 {min_confidence:.1%}",
                # "message": "請嘗試增加參考期數或降低信心度要求"
            # }), 400
        
        # # 取得歷史資料數量
        # sheets_manager = get_google_sheets_manager()
        # historical_data = []
        # if sheets_manager:
            # historical_data = sheets_manager.read_historical_data(sheet_name)
        
        # return jsonify({
            # "message": "預測完成",
            # "prediction": prediction,
            # "historical_data_count": len(historical_data),
            # "method_used": method,
            # "min_confidence_required": min_confidence,
            # "actual_confidence": prediction.get('confidence', 0)
        # })
    
    # except Exception as e:
        # return jsonify({"error": str(e)}), 500
def predict_lottery():
    """預測下一期大樂透號碼（使用 Google Sheets 資料和信心度閾值）"""
    try:
        data = request.get_json()
        periods = data.get('periods', 20)
        sheet_name = data.get('sheet_name', '大樂透資料')
        method = data.get('method', 'hybrid')
        min_confidence = data.get('min_confidence', 0.7)  # 預設最低信心度 70%
        total_predictions = data.get('total_predictions', 5)  # 新增欄位：預測幾組
        
        # 執行預測
        best_prediction, all_predictions = predict_numbers_from_sheets(
            sheet_name, periods, method, min_confidence, total_predictions
        )
        
        if not best_prediction:
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
            "message": f"成功從 {len(all_predictions)} 組中選出最佳預測",
            "best_prediction": best_prediction,
            "all_predictions": all_predictions,
            "historical_data_count": len(historical_data),
            "method_used": method,
            "min_confidence_required": min_confidence
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lottery_bp.route('/history', methods=['GET'])
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
        return jsonify({"error": str(e)}), 500


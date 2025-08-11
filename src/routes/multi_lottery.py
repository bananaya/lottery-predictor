#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多樂透遊戲 API 路由
支援所有樂透遊戲的 API 端點
"""
import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
import traceback

# 導入多樂透遊戲模組
from ..utils.multi_lottery_crawler import MultiLotteryCrawler
from ..utils.multi_google_sheets_manager import MultiLotteryGoogleSheetsManager
from ..utils.multi_prediction_algorithm import MultiLotteryPredictionAlgorithm

# 設定 logging 格式
logging.basicConfig(
    format="[%(asctime)s][%(name)-5s][%(levelname)-5s] %(message)s (%(filename)s:%(lineno)d)",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 建立藍圖
multi_lottery_bp = Blueprint('lottery', __name__)

# 初始化模組
crawler = MultiLotteryCrawler()
sheets_manager = MultiLotteryGoogleSheetsManager()
predictor = MultiLotteryPredictionAlgorithm()

@multi_lottery_bp.route('/games', methods=['GET'])
def get_supported_games():
    """獲取支援的樂透遊戲列表"""
    try:
        logging.info('Get support game.')
        games = crawler.get_supported_games()
        logging.info('Get support game completed.')
        game_info = {}
        
        for game in games:
            logging.info('Get game config.')
            config = crawler.get_game_config(game)
            logging.info(f'Get {config["name"]} config completed.')
            game_info[game] = {
                'name': config['name'],
                'number_range': config['number_range'],
                'number_count': config['number_count'],
                'special_number': config['special_number'],
                'special_range': config.get('special_range'),
                'is_digit_game': config.get('is_digit_game', False)
            }
        
        return jsonify({
            'success': True,
            'games': game_info,
            'total_games': len(games)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'獲取遊戲列表時發生錯誤: {str(e)}'
        }), 500

@multi_lottery_bp.route('/crawl', methods=['POST'])
def crawl_lottery_data():
    """爬取樂透資料"""
    try:
        data = request.get_json()
        game_type = data.get('game_type', 'lotto649')
        periods = data.get('periods', 20)
        sheet_name = data.get('sheet_name', '樂透資料')
        
        # 驗證遊戲類型
        if game_type not in crawler.get_supported_games():
            return jsonify({
                'success': False,
                'error': f'不支援的遊戲類型: {game_type}'
            }), 400
        
        # 爬取資料
        lottery_data = crawler.crawl_lottery_data(game_type, periods)
        
        if not lottery_data:
            return jsonify({
                'success': False,
                'error': f'無法獲取 {crawler.get_game_config(game_type)["name"]} 資料'
            }), 500
        
        # 儲存到 Google Sheets
        save_success = sheets_manager.save_lottery_data(sheet_name, game_type, lottery_data)
        
        return jsonify({
            'success': True,
            'message': f'成功爬取 {len(lottery_data)} 筆 {crawler.get_game_config(game_type)["name"]} 資料',
            'data_count': len(lottery_data),
            'game_type': crawler.get_game_config(game_type)['name'],
            'saved_to_sheets': save_success,
            'data': lottery_data[:5]  # 只返回前5筆作為預覽
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'爬取資料時發生錯誤: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@multi_lottery_bp.route('/predict', methods=['POST'])
def predict_numbers():
    """預測樂透號碼"""
    try:
        data = request.get_json()
        game_type = data.get('game_type', 'lotto649')
        periods = data.get('periods', 20)
        sheet_name = data.get('sheet_name', '樂透資料')
        min_confidence = data.get('min_confidence', 0.7)
        method = data.get('method', 'hybrid')
        
        # 驗證遊戲類型
        if game_type not in predictor.get_supported_games():
            return jsonify({
                'success': False,
                'error': f'不支援的遊戲類型: {game_type}'
            }), 400
        
        # 驗證預測方法
        valid_methods = ['frequency', 'pattern', 'hybrid', 'ml', 'advanced_statistical', 'neural_network']
        if method not in valid_methods:
            return jsonify({
                'success': False,
                'error': f'不支援的預測方法: {method}，支援的方法: {valid_methods}'
            }), 400
        
        # 優先從 Google Sheets 獲取資料
        historical_data = sheets_manager.get_lottery_data(sheet_name, game_type, periods)
        
        # 如果 Google Sheets 沒有足夠資料，嘗試爬取
        if len(historical_data) < 5:
            print(f"Google Sheets 資料不足({len(historical_data)}筆)，嘗試爬取資料...")
            crawled_data = crawler.crawl_lottery_data(game_type, periods)
            
            if crawled_data:
                # 儲存爬取的資料到 Google Sheets
                sheets_manager.save_lottery_data(sheet_name, game_type, crawled_data)
                historical_data = crawled_data
        
        num_predictions = data.get("num_predictions", 1)
        max_retries = data.get("max_retries", 1000)

        all_predictions = []
        for _ in range(num_predictions):
            best_prediction_this_round = None
            max_confidence_this_round = 0
            attempts = 0
            
            while attempts < max_retries:
                attempts += 1
                prediction_result = predictor.predict_numbers(
                    game_type, historical_data, method, min_confidence
                )
                
                if prediction_result["confidence"] > max_confidence_this_round:
                    max_confidence_this_round = prediction_result["confidence"]
                    best_prediction_this_round = prediction_result
                    
                if prediction_result["meets_confidence"]:
                    all_predictions.append(prediction_result)
                    break
            else: # If loop completes without breaking (min_confidence not met)
                if best_prediction_this_round:
                    all_predictions.append(best_prediction_this_round)
                
        if not all_predictions:
            return jsonify({
                'success': False,
                'error': '未能生成任何推薦號碼，請檢查參數或歷史資料。'
            }), 400

        # 準備預測結果
        game_config = predictor.get_game_config(game_type)
        predictions_to_save = []
        for pred in all_predictions:
            predictions_to_save.append({
                'game_type': game_config['name'],
                'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'method': pred['method'],
                'confidence': pred['confidence'],
                'periods_used': pred['data_count'],
                'predicted_numbers': pred['predicted_numbers'],
                'predicted_special': pred.get('predicted_special')
            })
        
        # 儲存預測結果到 Google Sheets
        sheets_manager.save_prediction_result(sheet_name, game_config['name'], predictions_to_save)
        
        # 返回給用戶的結果，如果沒有達到最低信心度，顯示信心度最高的推薦號碼
        response_predictions = []
        for pred in all_predictions:
            response_predictions.append({
                'predicted_numbers': pred['predicted_numbers'],
                'predicted_special': pred.get('predicted_special'),
                'confidence': pred['confidence'],
                'method': pred['method'],
                'data_count': pred['data_count'],
                'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify({
            'success': True,
            'game_type': game_config['name'],
            'method': method,
            'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'retry_count': attempts,
            'min_confidence': min_confidence,
            'predictions': response_predictions,
            'total_predictions_generated': len(response_predictions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'預測時發生錯誤: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@multi_lottery_bp.route('/history', methods=['POST'])
def get_historical_data():
    """獲取歷史開獎資料"""
    try:
        data = request.get_json()
        game_type = data.get('game_type', 'lotto649')
        periods = data.get('periods', 20)
        sheet_name = data.get('sheet_name', '樂透資料')
        
        # 驗證遊戲類型
        if game_type not in sheets_manager.get_supported_games():
            return jsonify({
                'success': False,
                'error': f'不支援的遊戲類型: {game_type}'
            }), 400
        
        # 從 Google Sheets 獲取資料
        historical_data = sheets_manager.get_lottery_data(sheet_name, game_type, periods)
        
        if not historical_data:
            return jsonify({
                'success': False,
                'error': f'未找到 {sheets_manager.get_game_config(game_type)["sheet_name"]} 資料',
                'suggestion': '請先爬取資料'
            }), 404
        
        return jsonify({
            'success': True,
            'game_type': sheets_manager.get_game_config(game_type)['sheet_name'].replace('資料', ''),
            'data_count': len(historical_data),
            'data': historical_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'獲取歷史資料時發生錯誤: {str(e)}'
        }), 500

@multi_lottery_bp.route('/prediction-history', methods=['POST'])
def get_prediction_history():
    """獲取預測歷史記錄"""
    try:
        data = request.get_json()
        game_type = data.get('game_type')  # 可選，不指定則獲取所有遊戲的預測記錄
        sheet_name = data.get('sheet_name', '樂透資料')
        limit = data.get('limit', 10)
        
        # 獲取預測歷史
        prediction_history = sheets_manager.get_prediction_history(sheet_name, game_type, limit)
        
        return jsonify({
            'success': True,
            'game_type': game_type or '所有遊戲',
            'history_count': len(prediction_history),
            'history': prediction_history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'獲取預測歷史時發生錯誤: {str(e)}'
        }), 500

@multi_lottery_bp.route('/health', methods=['GET'])
def health_check():
    """系統健康檢查"""
    try:
        # 檢查各模組狀態
        crawler_status = len(crawler.get_supported_games()) > 0
        sheets_status = sheets_manager.check_connection()
        predictor_status = len(predictor.get_supported_games()) > 0
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'modules': {
                'crawler': 'ok' if crawler_status else 'error',
                'google_sheets': 'ok' if sheets_status else 'warning',
                'predictor': 'ok' if predictor_status else 'error'
            },
            'supported_games': crawler.get_supported_games(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# 處理衍生樂透遊戲的特殊端點
@multi_lottery_bp.route('/derived-games', methods=['POST'])
def handle_derived_games():
    """處理衍生樂透遊戲（38樂合彩、49樂合彩）"""
    try:
        data = request.get_json()
        derived_game = data.get('derived_game')  # '38lotto' 或 '49lotto'
        periods = data.get('periods', 20)
        sheet_name = data.get('sheet_name', '樂透資料')
        
        if derived_game == '38lotto':
            # 38樂合彩基於今彩539
            base_game = 'dailycash'
            base_data = sheets_manager.get_lottery_data(sheet_name, base_game, periods)
            
            if not base_data:
                # 嘗試爬取今彩539資料
                base_data = crawler.crawl_lottery_data(base_game, periods)
                if base_data:
                    sheets_manager.save_lottery_data(sheet_name, base_game, base_data)
            
            # 生成38樂合彩資料
            derived_data = crawler.get_derived_lottery_data(base_game, derived_game, base_data)
            
        elif derived_game == '49lotto':
            # 49樂合彩基於大樂透
            base_game = 'lotto649'
            base_data = sheets_manager.get_lottery_data(sheet_name, base_game, periods)
            
            if not base_data:
                # 嘗試爬取大樂透資料
                base_data = crawler.crawl_lottery_data(base_game, periods)
                if base_data:
                    sheets_manager.save_lottery_data(sheet_name, base_game, base_data)
            
            # 生成49樂合彩資料
            derived_data = crawler.get_derived_lottery_data(base_game, derived_game, base_data)
            
        else:
            return jsonify({
                'success': False,
                'error': f'不支援的衍生遊戲: {derived_game}'
            }), 400
        
        # 儲存衍生遊戲資料
        if derived_data:
            sheets_manager.save_lottery_data(sheet_name, derived_game, derived_data)
        
        return jsonify({
            'success': True,
            'derived_game': derived_game,
            'base_game': base_game,
            'data_count': len(derived_data),
            'data': derived_data[:5]  # 只返回前5筆作為預覽
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'處理衍生遊戲時發生錯誤: {str(e)}'
        }), 500


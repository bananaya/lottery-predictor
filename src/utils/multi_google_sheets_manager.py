#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多樂透遊戲 Google Sheets 管理器
處理所有樂透遊戲的 Google Sheets 相關操作
"""

import os
import json
from typing import List, Dict, Optional, Any
import gspread
from google.oauth2.service_account import Credentials

class MultiLotteryGoogleSheetsManager:
    """多樂透遊戲 Google Sheets 管理器"""
    
    def __init__(self):
        """初始化 Google Sheets 管理器"""
        self.client = None
        self.credentials = None
        self._initialize_client()
        
        # 樂透遊戲工作表配置
        self.game_sheet_configs = {
            'lotto649': {
                'sheet_name': '大樂透資料',
                'headers': ['期別', '開獎日期', '號碼1', '號碼2', '號碼3', '號碼4', '號碼5', '號碼6', '特別號'],
                'number_columns': ['號碼1', '號碼2', '號碼3', '號碼4', '號碼5', '號碼6'],
                'special_column': '特別號'
            },
            'superlotto638': {
                'sheet_name': '威力彩資料',
                'headers': ['期別', '開獎日期', '號碼1', '號碼2', '號碼3', '號碼4', '號碼5', '號碼6', '第二區號碼'],
                'number_columns': ['號碼1', '號碼2', '號碼3', '號碼4', '號碼5', '號碼6'],
                'special_column': '第二區號碼'
            },
            'dailycash': {
                'sheet_name': '今彩539資料',
                'headers': ['期別', '開獎日期', '號碼1', '號碼2', '號碼3', '號碼4', '號碼5'],
                'number_columns': ['號碼1', '號碼2', '號碼3', '號碼4', '號碼5'],
                'special_column': None
            },
            # 'lotto1224': {
                # 'sheet_name': '雙贏彩資料',
                # 'headers': ['期別', '開獎日期', '號碼1', '號碼2', '號碼3', '號碼4', '號碼5', '號碼6', 
                           # '號碼7', '號碼8', '號碼9', '號碼10', '號碼11', '號碼12'],
                # 'number_columns': ['號碼1', '號碼2', '號碼3', '號碼4', '號碼5', '號碼6', 
                                  # '號碼7', '號碼8', '號碼9', '號碼10', '號碼11', '號碼12'],
                # 'special_column': None
            # },
            '3stars': {
                'sheet_name': '3星彩資料',
                'headers': ['期別', '開獎日期', '百位', '十位', '個位'],
                'number_columns': ['百位', '十位', '個位'],
                'special_column': None
            },
            '4stars': {
                'sheet_name': '4星彩資料',
                'headers': ['期別', '開獎日期', '千位', '百位', '十位', '個位'],
                'number_columns': ['千位', '百位', '十位', '個位'],
                'special_column': None
            },
            'bingobingo': {
                'sheet_name': 'BINGO BINGO資料',
                'headers': ['期別', '開獎日期'] + [f'號碼{i}' for i in range(1, 21)],
                'number_columns': [f'號碼{i}' for i in range(1, 21)],
                'special_column': None
            },
            '39lotto': {
                'sheet_name': '39樂合彩資料',
                'headers': ['期別', '開獎日期', '號碼1', '號碼2', '號碼3', '號碼4', '號碼5'],
                'number_columns': ['號碼1', '號碼2', '號碼3', '號碼4', '號碼5'],
                'special_column': None
            },
            '49lotto': {
                'sheet_name': '49樂合彩資料',
                'headers': ['期別', '開獎日期', '號碼1', '號碼2', '號碼3', '號碼4', '號碼5', '號碼6'],
                'number_columns': ['號碼1', '號碼2', '號碼3', '號碼4', '號碼5', '號碼6'],
                'special_column': None
            },
            'predictions': {
                'sheet_name': '預測結果',
                'headers': ['遊戲類型', '預測日期', '預測方法', '信心度', '參考期數', '號碼', '特別號'],
                'number_columns': [],
                'special_column': None
            }
        }
    
    def _initialize_client(self):
        """初始化 Google Sheets 客戶端"""
        try:
            # 從環境變數獲取服務帳戶金鑰
            service_account_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
            
            if service_account_key:
                # 解析 JSON 金鑰
                credentials_dict = json.loads(service_account_key)
                
                # 設定權限範圍
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                
                # 建立認證
                self.credentials = Credentials.from_service_account_info(
                    credentials_dict, scopes=scope
                )
                
                # 建立客戶端
                self.client = gspread.authorize(self.credentials)
                
                print("Google Sheets 客戶端初始化成功")
                
            else:
                print("警告：未找到 Google Sheets 服務帳戶金鑰")
                
        except Exception as e:
            print(f"初始化 Google Sheets 客戶端時發生錯誤: {e}")
    
    def get_game_config(self, game_type: str) -> Dict:
        """獲取遊戲工作表配置"""
        if game_type not in self.game_sheet_configs:
            raise ValueError(f"不支援的遊戲類型: {game_type}")
        return self.game_sheet_configs[game_type]
    
    def get_supported_games(self) -> List[str]:
        """獲取支援的遊戲列表"""
        return [game for game in self.game_sheet_configs.keys() if game != 'predictions']
    
    def create_or_get_worksheet(self, spreadsheet_name: str, game_type: str) -> Optional[Any]:
        """建立或獲取工作表"""
        try:
            if not self.client:
                print("Google Sheets 客戶端未初始化")
                return None
            
            config = self.get_game_config(game_type)
            worksheet_name = config['sheet_name']
            
            # 嘗試開啟試算表
            try:
                spreadsheet = self.client.open(spreadsheet_name)
            except gspread.SpreadsheetNotFound:
                # 建立新的試算表
                spreadsheet = self.client.create(spreadsheet_name)
                print(f"建立新的試算表: {spreadsheet_name}")
            
            # 嘗試獲取工作表
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                print(f"找到現有工作表: {worksheet_name}")
            except gspread.WorksheetNotFound:
                # 建立新的工作表
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=1000,
                    cols=len(config['headers'])
                )
                
                # 設定表頭
                worksheet.append_row(config['headers'])
                print(f"建立新的工作表: {worksheet_name}")
            
            return worksheet
            
        except Exception as e:
            print(f"建立或獲取工作表時發生錯誤: {e}")
            return None
    
    def save_lottery_data(self, spreadsheet_name: str, game_type: str, data: List[Dict]) -> bool:
        """儲存樂透資料到 Google Sheets"""
        try:
            worksheet = self.create_or_get_worksheet(spreadsheet_name, game_type)
            if not worksheet:
                return False
            
            config = self.get_game_config(game_type)
            
            # 獲取現有資料以避免重複
            existing_data = worksheet.get_all_records()
            existing_periods = {row.get('期別', '') for row in existing_data}
            
            # 準備要新增的資料
            new_rows = []
            for item in data:
                if item.get('period', '') not in existing_periods:
                    row = [item.get('period', ''), item.get('date', '')]
                    
                    # 新增號碼欄位
                    numbers = item.get('numbers', [])
                    for i, col in enumerate(config['number_columns']):
                        if i < len(numbers):
                            row.append(numbers[i])
                        else:
                            row.append('')
                    
                    # 新增特別號欄位（如果有）
                    if config['special_column']:
                        special_number = item.get('special_number', '')
                        row.append(special_number)
                    
                    new_rows.append(row)
            
            # 批次新增資料
            if new_rows:
                worksheet.append_rows(new_rows)
                print(f"成功儲存 {len(new_rows)} 筆 {config['sheet_name']} 資料")
                return True
            else:
                print(f"沒有新的 {config['sheet_name']} 資料需要儲存")
                return True
                
        except Exception as e:
            print(f"儲存 {game_type} 資料時發生錯誤: {e}")
            return False
    
    def get_lottery_data(self, spreadsheet_name: str, game_type: str, periods: int = 20) -> List[Dict]:
        """從 Google Sheets 獲取樂透資料"""
        try:
            worksheet = self.create_or_get_worksheet(spreadsheet_name, game_type)
            if not worksheet:
                return []
            
            config = self.get_game_config(game_type)
            
            # 獲取所有資料
            all_records = worksheet.get_all_records()
            
            # 轉換為標準格式
            results = []
            for record in all_records[-periods:]:  # 獲取最近的期數
                numbers = []
                for col in config['number_columns']:
                    if col in record and record[col] is not None and record[col] != '':
                        try:
                            numbers.append(int(record[col]))
                        except (ValueError, TypeError):
                            pass
                
                if numbers:
                    result = {
                        'period': str(record.get('期別', '')),
                        'date': str(record.get('開獎日期', '')),
                        'numbers': numbers,
                        'game_type': config['sheet_name'].replace('資料', '')
                    }
                    
                    # 新增特別號（如果有）
                    if config['special_column'] and config['special_column'] in record:
                        special_number = record[config['special_column']]
                        if special_number:
                            try:
                                result['special_number'] = int(special_number)
                            except (ValueError, TypeError):
                                pass
                    
                    results.append(result)
            
            print(f"從 Google Sheets 獲取 {len(results)} 筆 {config['sheet_name']} 資料")
            return results
            
        except Exception as e:
            print(f"獲取 {game_type} 資料時發生錯誤: {e}")
            return []
    
    def save_prediction_result(self, spreadsheet_name: str, game_type: str, prediction_results: List[Dict]) -> bool:
        """儲存預測結果到 Google Sheets"""
        try:
            worksheet = self.create_or_get_worksheet(spreadsheet_name, 'predictions')
            if not worksheet:
                return False
            
            rows_to_append = []
            for prediction_data in prediction_results:
                row = [
                    prediction_data.get('game_type', ''),
                    prediction_data.get('prediction_date', ''),
                    prediction_data.get('method', ''),
                    prediction_data.get('confidence', ''),
                    prediction_data.get('periods_used', ''),
                    ', '.join(map(str, prediction_data.get('predicted_numbers', []))),
                    str(prediction_data.get('predicted_special', ''))
                ]
                rows_to_append.append(row)
                
            if rows_to_append:
                worksheet.append_rows(rows_to_append)
                print(f"成功儲存 {len(rows_to_append)} 筆 {game_type} 預測結果")
            return True
            
        except Exception as e:
            print(f"儲存預測結果時發生錯誤: {e}")
            return False
    
    def get_prediction_history(self, spreadsheet_name: str, game_type: str = None, limit: int = 10) -> List[Dict]:
        """獲取預測歷史記錄"""
        try:
            worksheet = self.create_or_get_worksheet(spreadsheet_name, 'predictions')
            if not worksheet:
                return []
            
            # 獲取所有預測記錄
            all_records = worksheet.get_all_records()
            
            # 過濾特定遊戲類型（如果指定）
            if game_type:
                filtered_records = [r for r in all_records if r.get('遊戲類型') == game_type]
            else:
                filtered_records = all_records
            
            # 返回最近的記錄
            return filtered_records[-limit:]
            
        except Exception as e:
            print(f"獲取預測歷史時發生錯誤: {e}")
            return []
    
    def check_connection(self) -> bool:
        """檢查 Google Sheets 連線狀態"""
        try:
            if not self.client:
                return False
            
            # 嘗試列出試算表（測試連線）
            self.client.list_permissions('test')
            return True
            
        except Exception:
            return False


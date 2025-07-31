import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime

class GoogleSheetsManager:
    """Google Sheets 資料管理類別"""
    
    def __init__(self):
        self.gc = None
        self.sheet = None
        self._authenticate()
    
    def _authenticate(self):
        """Google Sheets API 認證"""
        try:
            # 從環境變數取得服務帳戶金鑰
            service_account_key = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            
            if service_account_key:
                # 解析 JSON 金鑰
                credentials_dict = json.loads(service_account_key)
                
                # 設定權限範圍
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                
                # 建立認證
                credentials = Credentials.from_service_account_info(
                    credentials_dict, scopes=scope
                )
                
                # 建立 gspread 客戶端
                self.gc = gspread.authorize(credentials)
                print("Google Sheets API 認證成功")
                return True
            else:
                print("未找到 GOOGLE_SERVICE_ACCOUNT_KEY 環境變數")
                return False
                
        except Exception as e:
            print(f"Google Sheets 認證失敗: {e}")
            return False
    
    def get_or_create_sheet(self, sheet_name):
        """取得或建立試算表"""
        try:
            if not self.gc:
                print("Google Sheets 未認證")
                return None
            
            # 嘗試開啟現有試算表
            try:
                self.sheet = self.gc.open(sheet_name)
                print(f"成功開啟試算表: {sheet_name}")
            except gspread.SpreadsheetNotFound:
                # 如果試算表不存在，建立新的
                self.sheet = self.gc.create(sheet_name)
                print(f"成功建立新試算表: {sheet_name}")
            
            return self.sheet
            
        except Exception as e:
            print(f"取得或建立試算表失敗: {e}")
            return None
    
    def get_or_create_worksheet(self, worksheet_name, headers=None):
        """取得或建立工作表"""
        try:
            if not self.sheet:
                print("試算表未初始化")
                return None
            
            # 嘗試取得現有工作表
            try:
                worksheet = self.sheet.worksheet(worksheet_name)
                print(f"成功取得工作表: {worksheet_name}")
            except gspread.WorksheetNotFound:
                # 如果工作表不存在，建立新的
                worksheet = self.sheet.add_worksheet(
                    title=worksheet_name, 
                    rows=1000, 
                    cols=20
                )
                print(f"成功建立新工作表: {worksheet_name}")
                
                # 如果提供了標題，設定第一行
                if headers:
                    worksheet.append_row(headers)
                    print(f"設定工作表標題: {headers}")
            
            return worksheet
            
        except Exception as e:
            print(f"取得或建立工作表失敗: {e}")
            return None
    
    def read_historical_data(self, sheet_name, worksheet_name="歷史開獎資料"):
        """從 Google Sheets 讀取歷史資料"""
        try:
            # 取得試算表和工作表
            sheet = self.get_or_create_sheet(sheet_name)
            if not sheet:
                return []
            
            worksheet = self.get_or_create_worksheet(
                worksheet_name,
                headers=["期數", "開獎日期", "號碼1", "號碼2", "號碼3", "號碼4", "號碼5", "號碼6", "特別號", "遊戲類型"]
            )
            if not worksheet:
                return []
            
            # 取得所有資料
            all_records = worksheet.get_all_records()
            
            # 轉換為標準格式
            historical_data = []
            for record in all_records:
                if record.get("期數") and record.get("號碼1"):  # 確保有有效資料
                    try:
                        numbers = [
                            int(record.get("號碼1", 0)),
                            int(record.get("號碼2", 0)),
                            int(record.get("號碼3", 0)),
                            int(record.get("號碼4", 0)),
                            int(record.get("號碼5", 0)),
                            int(record.get("號碼6", 0))
                        ]
                        
                        # 過濾無效號碼
                        numbers = [n for n in numbers if 1 <= n <= 49]
                        
                        if len(numbers) == 6:  # 確保有6個有效號碼
                            data_entry = {
                                "period": str(record.get("期數", "")),
                                "date": str(record.get("開獎日期", "")),
                                "numbers": sorted(numbers),
                                "special_number": int(record.get("特別號", 1)),
                                "game_type": str(record.get("遊戲類型", "大樂透"))
                            }
                            historical_data.append(data_entry)
                    except (ValueError, TypeError) as e:
                        print(f"跳過無效資料行: {record}, 錯誤: {e}")
                        continue
            
            print(f"從 Google Sheets 讀取到 {len(historical_data)} 筆歷史資料")
            return historical_data
            
        except Exception as e:
            print(f"讀取歷史資料失敗: {e}")
            return []
    
    def save_historical_data(self, sheet_name, data, worksheet_name="歷史開獎資料"):
        """儲存歷史資料到 Google Sheets"""
        try:
            # 取得試算表和工作表
            sheet = self.get_or_create_sheet(sheet_name)
            if not sheet:
                return False
            
            worksheet = self.get_or_create_worksheet(
                worksheet_name,
                headers=["期數", "開獎日期", "號碼1", "號碼2", "號碼3", "號碼4", "號碼5", "號碼6", "特別號", "遊戲類型"]
            )
            if not worksheet:
                return False
            
            # 取得現有資料以避免重複
            existing_records = worksheet.get_all_records()
            existing_periods = {str(record.get("期數", "")) for record in existing_records}
            
            # 準備新資料
            new_rows = []
            for entry in data:
                period = str(entry.get("period", ""))
                if period and period not in existing_periods:
                    numbers = entry.get("numbers", [])
                    if len(numbers) >= 6:
                        row = [
                            period,
                            entry.get("date", ""),
                            numbers[0] if len(numbers) > 0 else "",
                            numbers[1] if len(numbers) > 1 else "",
                            numbers[2] if len(numbers) > 2 else "",
                            numbers[3] if len(numbers) > 3 else "",
                            numbers[4] if len(numbers) > 4 else "",
                            numbers[5] if len(numbers) > 5 else "",
                            entry.get("special_number", ""),
                            entry.get("game_type", "大樂透")
                        ]
                        new_rows.append(row)
            
            # 批次新增資料
            if new_rows:
                worksheet.append_rows(new_rows)
                print(f"成功儲存 {len(new_rows)} 筆新的歷史資料")
            else:
                print("沒有新的歷史資料需要儲存")
            
            return True
            
        except Exception as e:
            print(f"儲存歷史資料失敗: {e}")
            return False
    
    def save_prediction_result(self, sheet_name, prediction, worksheet_name="預測結果"):
        """儲存預測結果到 Google Sheets"""
        try:
            # 取得試算表和工作表
            sheet = self.get_or_create_sheet(sheet_name)
            if not sheet:
                return False
            
            worksheet = self.get_or_create_worksheet(
                worksheet_name,
                headers=["預測日期", "號碼1", "號碼2", "號碼3", "號碼4", "號碼5", "號碼6", "特別號", "信心度", "預測方法"]
            )
            if not worksheet:
                return False
            
            # 準備預測資料
            numbers = prediction.get("predicted_numbers", [])
            if len(numbers) >= 6:
                row = [
                    prediction.get("prediction_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    numbers[0] if len(numbers) > 0 else "",
                    numbers[1] if len(numbers) > 1 else "",
                    numbers[2] if len(numbers) > 2 else "",
                    numbers[3] if len(numbers) > 3 else "",
                    numbers[4] if len(numbers) > 4 else "",
                    numbers[5] if len(numbers) > 5 else "",
                    prediction.get("predicted_special", ""),
                    prediction.get("confidence", ""),
                    prediction.get("method", "")
                ]
                
                worksheet.append_row(row)
                print("成功儲存預測結果")
                return True
            else:
                print("預測資料格式不正確")
                return False
            
        except Exception as e:
            print(f"儲存預測結果失敗: {e}")
            return False
    
    def get_sheet_info(self, sheet_name):
        """取得試算表資訊"""
        try:
            sheet = self.get_or_create_sheet(sheet_name)
            if not sheet:
                return None
            
            worksheets = sheet.worksheets()
            info = {
                "sheet_name": sheet_name,
                "sheet_id": sheet.id,
                "sheet_url": sheet.url,
                "worksheets": []
            }
            
            for ws in worksheets:
                ws_info = {
                    "title": ws.title,
                    "rows": ws.row_count,
                    "cols": ws.col_count,
                    "data_rows": len(ws.get_all_records())
                }
                info["worksheets"].append(ws_info)
            
            return info
            
        except Exception as e:
            print(f"取得試算表資訊失敗: {e}")
            return None


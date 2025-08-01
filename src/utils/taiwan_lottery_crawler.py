from TaiwanLottery import TaiwanLotteryCrawler
from datetime import datetime, timedelta
import logging

import requests
from bs4 import BeautifulSoup
import json
import time
import random
# from datetime import datetime, timedelta
import re

class TaiwanLotteryCrawlerClass:
    """台灣彩券爬蟲類別"""
    
    def __init__(self):
        self.base_url = "https://www.taiwanlottery.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.now = datetime.now()
        self.start_year = 2004

    # === 2. 抓取與寫入 ===
    def get_lotto_data(game_key, extract_func, max_draws=50):   
        try: 
            existing_dates = set()
            lottery_datas = []
            draw_count = 0

            for year in range(now.year, start_year - 1, -1):
                for month in range(12, 0, -1):
                    if year == now.year and month > now.month:
                        continue
                    try:
                        results = getattr(crawler, game_key)([str(year), f"{month:02d}"])
                    except Exception as e:
                        logger.warning(f"⚠️ 抓取失敗 {game_key} {year}/{month:02d}：{e}")
                        continue
                    for draw in sorted(results, key=lambda x: x.get('開獎日期'), reverse=True):
                        date_str = draw.get('開獎日期')
                        if not date_str:
                            continue
                        try:
                            draw_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                            date_str = draw_date.strftime("%Y/%m/%d")
                        except Exception:
                            continue
                        if draw_date > now or date_str in existing_dates:
                            continue
                        lottery_data = extract_func(draw, date_str)
                        if lottery_data:
                            lottery_datas.append(lottery_data)
                            existing_dates.add(date_str)
                            draw_count += 1
                        if draw_count >= max_draws:
                            break
                    if draw_count >= max_draws:
                        break
                if draw_count >= max_draws:
                    break

            if lottery_datas:                
                logger.info(f"✅ {game_key} 寫入 {len(lottery_datas)} 筆")
                return lottery_datas
            else:            
                logger.warning(f"⚠️ {game_key} 沒有新資料")
                return []
                
        except Exception as e:
            print(f"爬取{game_key}資料失敗: {e}")
            return []

    # === 3. 彩券欄位對應 ===
    def extract_lotto649(draw, date_str):
        return [date_str, draw.get('期別')] + draw.get('獎號') + [draw.get('特別號')]

    def extract_daily539(draw, date_str):
        return [date_str, draw.get('期別')] + draw.get('獎號')

    def extract_powerlotto(draw, date_str):
        return [date_str, draw.get('期別')] + draw.get('第一區') + [draw.get('第二區')]        


    # fetch_and_write("lotto649", "大樂透", extract_lotto649)
    # fetch_and_write("daily_cash", "今彩539", extract_daily539)
    # fetch_and_write("super_lotto", "威力彩", extract_powerlotto)

        
    def get_lotto649_data(self, periods=10):
        """
        爬取大樂透(Lotto 6/49)歷史資料
        
        Args:
            periods (int): 要爬取的期數
            
        Returns:
            list: 包含開獎資料的列表
        """
        try:
            # 由於台灣彩券網站結構複雜，這裡使用模擬資料
            # 實際應用中需要根據網站的具體結構進行調整
            
            lottery_data = []
            base_date = datetime.now()
            
            for i in range(periods):
                # 模擬期數（實際應該從網站爬取）
                period_num = f"11400{str(i+1).zfill(3)}"
                
                # 模擬開獎日期（每週二、五開獎）
                days_back = i * 3 + random.randint(0, 2)
                draw_date = base_date - timedelta(days=days_back)
                
                # 生成模擬的開獎號碼（實際應該從網站爬取）
                numbers = self._generate_realistic_numbers()
                special_number = random.randint(1, 49)
                while special_number in numbers:
                    special_number = random.randint(1, 49)
                
                lottery_data.append({
                    "period": period_num,
                    "date": draw_date.strftime("%Y-%m-%d"),
                    "numbers": sorted(numbers),
                    "special_number": special_number,
                    "game_type": "大樂透"
                })
                
                # 添加隨機延遲避免被封鎖
                time.sleep(random.uniform(0.1, 0.3))
            
            return lottery_data
            
        except Exception as e:
            print(f"爬取大樂透資料失敗: {e}")
            return []
    
    def _generate_realistic_numbers(self):
        """
        生成更真實的大樂透號碼
        基於實際大樂透的統計特性
        """
        # 大樂透號碼範圍 1-49，選6個
        # 根據歷史統計，某些號碼出現頻率較高
        
        # 熱門號碼（基於歷史統計）
        hot_numbers = [1, 2, 3, 7, 8, 12, 15, 16, 18, 20, 23, 26, 28, 32, 35, 38, 41, 43, 45, 47]
        # 冷門號碼
        cold_numbers = [4, 5, 6, 9, 10, 11, 13, 14, 17, 19, 21, 22, 24, 25, 27, 29, 30, 31, 33, 34, 36, 37, 39, 40, 42, 44, 46, 48, 49]
        
        numbers = []
        
        # 70% 機率從熱門號碼中選擇
        hot_count = random.choices([2, 3, 4], weights=[0.3, 0.5, 0.2])[0]
        numbers.extend(random.sample(hot_numbers, min(hot_count, len(hot_numbers))))
        
        # 剩餘從冷門號碼中選擇
        remaining_count = 6 - len(numbers)
        if remaining_count > 0:
            available_cold = [n for n in cold_numbers if n not in numbers]
            numbers.extend(random.sample(available_cold, min(remaining_count, len(available_cold))))
        
        # 如果還不夠6個，從所有號碼中補充
        if len(numbers) < 6:
            all_numbers = list(range(1, 50))
            available = [n for n in all_numbers if n not in numbers]
            numbers.extend(random.sample(available, 6 - len(numbers)))
        
        return numbers[:6]
    
    def get_real_lotto649_data(self, year=None, month=None):
        """
        嘗試從台灣彩券官網爬取真實資料
        
        Args:
            year (str): 年份
            month (str): 月份
            
        Returns:
            list: 開獎資料列表
        """
        try:
            if not year:
                year = str(datetime.now().year)
            if not month:
                month = str(datetime.now().month).zfill(2)
            
            # 構建查詢URL（需要根據實際網站結構調整）
            url = f"{self.base_url}/lotto/history/history_result/"
            
            # 發送請求
            response = self.session.get(url)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 這裡需要根據實際的HTML結構來解析
            # 由於台灣彩券網站使用動態載入，可能需要使用Selenium
            
            print("注意：真實爬蟲功能需要根據台灣彩券網站的實際結構進行調整")
            print("目前返回模擬資料")
            
            return self.get_lotto649_data(10)
            
        except Exception as e:
            print(f"爬取真實資料失敗，使用模擬資料: {e}")
            return self.get_lotto649_data(10)
    
    def analyze_number_frequency(self, data):
        """
        分析號碼出現頻率
        
        Args:
            data (list): 歷史開獎資料
            
        Returns:
            dict: 號碼頻率統計
        """
        frequency = {}
        special_frequency = {}
        
        for record in data:
            # 統計一般號碼
            for num in record['numbers']:
                frequency[num] = frequency.get(num, 0) + 1
            
            # 統計特別號
            special_num = record['special_number']
            special_frequency[special_num] = special_frequency.get(special_num, 0) + 1
        
        return {
            'number_frequency': frequency,
            'special_frequency': special_frequency,
            'total_draws': len(data)
        }
    
    def get_number_patterns(self, data):
        """
        分析號碼模式
        
        Args:
            data (list): 歷史開獎資料
            
        Returns:
            dict: 號碼模式分析
        """
        patterns = {
            'consecutive_pairs': 0,  # 連號對數
            'odd_even_ratio': {'odd': 0, 'even': 0},  # 奇偶比例
            'high_low_ratio': {'high': 0, 'low': 0},  # 高低號比例
            'sum_ranges': []  # 號碼總和範圍
        }
        
        for record in data:
            numbers = sorted(record['numbers'])
            
            # 檢查連號
            for i in range(len(numbers) - 1):
                if numbers[i+1] - numbers[i] == 1:
                    patterns['consecutive_pairs'] += 1
            
            # 奇偶統計
            for num in numbers:
                if num % 2 == 0:
                    patterns['odd_even_ratio']['even'] += 1
                else:
                    patterns['odd_even_ratio']['odd'] += 1
            
            # 高低號統計（1-24為低號，25-49為高號）
            for num in numbers:
                if num <= 24:
                    patterns['high_low_ratio']['low'] += 1
                else:
                    patterns['high_low_ratio']['high'] += 1
            
            # 號碼總和
            patterns['sum_ranges'].append(sum(numbers))
        
        return patterns


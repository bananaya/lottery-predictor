#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多樂透遊戲爬蟲模組
支援台灣彩券所有樂透遊戲的資料爬取
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import random
from typing import List, Dict, Optional, Tuple

class MultiLotteryCrawler:
    """多樂透遊戲爬蟲類別"""
    
    def __init__(self):
        """初始化爬蟲"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 樂透遊戲配置
        self.game_configs = {
            'lotto649': {
                'name': '大樂透',
                'url': 'https://www.taiwanlottery.com/lotto/lotto649/history.aspx',
                'number_range': (1, 49),
                'number_count': 6,
                'special_number': True,
                'special_range': (1, 49)
            },
            'superlotto638': {
                'name': '威力彩',
                'url': 'https://www.taiwanlottery.com/lotto/superlotto638/history.aspx',
                'number_range': (1, 38),
                'number_count': 6,
                'special_number': True,
                'special_range': (1, 8)
            },
            'dailycash': {
                'name': '今彩539',
                'url': 'https://www.taiwanlottery.com/lotto/dailycash/history.aspx',
                'number_range': (1, 39),
                'number_count': 5,
                'special_number': False,
                'special_range': None
            },
            'lotto1224': {
                'name': '雙贏彩',
                'url': 'https://www.taiwanlottery.com/lotto/lotto1224/history.aspx',
                'number_range': (1, 24),
                'number_count': 12,
                'special_number': False,
                'special_range': None
            },
            '3stars': {
                'name': '3星彩',
                'url': 'https://www.taiwanlottery.com/lotto/3stars/history.aspx',
                'number_range': (0, 9),
                'number_count': 3,
                'special_number': False,
                'special_range': None,
                'is_digit_game': True
            },
            '4stars': {
                'name': '4星彩',
                'url': 'https://www.taiwanlottery.com/lotto/4stars/history.aspx',
                'number_range': (0, 9),
                'number_count': 4,
                'special_number': False,
                'special_range': None,
                'is_digit_game': True
            },
            'bingobingo': {
                'name': 'BINGO BINGO 賓果賓果',
                'url': 'https://www.taiwanlottery.com/lotto/bingobingo/history.aspx',
                'number_range': (1, 80),
                'number_count': 20,
                'special_number': False,
                'special_range': None
            }
        }
    
    def get_game_config(self, game_type: str) -> Dict:
        """獲取遊戲配置"""
        if game_type not in self.game_configs:
            raise ValueError(f"不支援的遊戲類型: {game_type}")
        return self.game_configs[game_type]
    
    def get_supported_games(self) -> List[str]:
        """獲取支援的遊戲列表"""
        return list(self.game_configs.keys())
    
    def crawl_lottery_data(self, game_type: str, periods: int = 20) -> List[Dict]:
        """
        爬取樂透資料
        
        Args:
            game_type: 遊戲類型
            periods: 要爬取的期數
            
        Returns:
            包含開獎資料的字典列表
        """
        config = self.get_game_config(game_type)
        
        # 根據遊戲類型選擇爬取方法
        if game_type in ['lotto649', 'superlotto638', 'dailycash', 'lotto1224']:
            return self._crawl_standard_lottery(game_type, periods)
        elif game_type in ['3stars', '4stars']:
            return self._crawl_star_lottery(game_type, periods)
        elif game_type == 'bingobingo':
            return self._crawl_bingo_lottery(periods)
        else:
            raise ValueError(f"未實作的遊戲類型: {game_type}")
    
    def _crawl_standard_lottery(self, game_type: str, periods: int) -> List[Dict]:
        """爬取標準樂透遊戲資料（大樂透、威力彩、今彩539、雙贏彩）"""
        config = self.get_game_config(game_type)
        results = []
        
        try:
            # 使用台灣彩券官方網站的歷史開獎結果頁面
            url = f"https://www.taiwanlottery.com/lotto/result/{game_type}/"
            
            # 模擬瀏覽器請求
            time.sleep(random.uniform(1, 3))  # 隨機延遲
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析開獎結果表格
            table = soup.find('table', class_='table')
            if not table:
                # 嘗試其他可能的表格選擇器
                table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:]  # 跳過表頭
                
                for i, row in enumerate(rows[:periods]):
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        # 解析期別
                        period = cols[0].get_text(strip=True)
                        
                        # 解析開獎日期
                        date_text = cols[1].get_text(strip=True)
                        draw_date = self._parse_date(date_text)
                        
                        # 解析開獎號碼
                        numbers_text = cols[2].get_text(strip=True)
                        numbers, special_number = self._parse_numbers(numbers_text, config)
                        
                        if numbers:
                            result = {
                                'period': period,
                                'date': draw_date,
                                'numbers': numbers,
                                'game_type': config['name']
                            }
                            
                            if special_number is not None:
                                result['special_number'] = special_number
                            
                            results.append(result)
            
            # 如果官方網站無法獲取資料，使用備用資料源
            if not results:
                results = self._crawl_backup_source(game_type, periods)
                
        except Exception as e:
            print(f"爬取 {config['name']} 資料時發生錯誤: {e}")
            # 嘗試備用資料源
            results = self._crawl_backup_source(game_type, periods)
        
        return results
    
    def _crawl_star_lottery(self, game_type: str, periods: int) -> List[Dict]:
        """爬取星彩遊戲資料（3星彩、4星彩）"""
        config = self.get_game_config(game_type)
        results = []
        
        try:
            # 使用第三方資料源
            if game_type == '3stars':
                url = "https://www.pilio.idv.tw/lto/list3.asp"
            else:  # 4stars
                url = "https://www.pilio.idv.tw/lto/list4.asp"
            
            time.sleep(random.uniform(1, 3))
            response = self.session.get(url, timeout=10)
            response.encoding = 'big5'  # 設定正確的編碼
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析開獎結果
            rows = soup.find_all('tr')
            
            for row in rows[1:periods+1]:  # 跳過表頭
                cols = row.find_all('td')
                if len(cols) >= 2:
                    # 解析日期
                    date_text = cols[0].get_text(strip=True)
                    draw_date = self._parse_date(date_text)
                    
                    # 解析號碼
                    numbers_text = cols[1].get_text(strip=True)
                    numbers = self._parse_star_numbers(numbers_text, config['number_count'])
                    
                    if numbers:
                        # 生成期別（星彩遊戲通常沒有明確的期別）
                        period = f"{draw_date.replace('-', '')}"
                        
                        result = {
                            'period': period,
                            'date': draw_date,
                            'numbers': numbers,
                            'game_type': config['name']
                        }
                        
                        results.append(result)
                        
        except Exception as e:
            print(f"爬取 {config['name']} 資料時發生錯誤: {e}")
        
        return results
    
    def _crawl_bingo_lottery(self, periods: int) -> List[Dict]:
        """爬取 BINGO BINGO 賓果賓果資料"""
        results = []
        
        try:
            # BINGO BINGO 由於開獎頻率高，只獲取最近的資料
            url = "https://www.taiwanlottery.com/lotto/result/bingo_bingo/"
            
            time.sleep(random.uniform(1, 3))
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析開獎結果表格
            table = soup.find('table', class_='table')
            if table:
                rows = table.find_all('tr')[1:]  # 跳過表頭
                
                for i, row in enumerate(rows[:periods]):
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        # 解析期別
                        period = cols[0].get_text(strip=True)
                        
                        # 解析開獎時間
                        datetime_text = cols[1].get_text(strip=True)
                        draw_date = self._parse_datetime(datetime_text)
                        
                        # 解析開獎號碼（20個號碼）
                        numbers_text = cols[2].get_text(strip=True)
                        numbers = self._parse_bingo_numbers(numbers_text)
                        
                        if numbers:
                            result = {
                                'period': period,
                                'date': draw_date,
                                'numbers': numbers,
                                'game_type': 'BINGO BINGO 賓果賓果'
                            }
                            
                            results.append(result)
                            
        except Exception as e:
            print(f"爬取 BINGO BINGO 賓果賓果資料時發生錯誤: {e}")
        
        return results
    
    def _crawl_backup_source(self, game_type: str, periods: int) -> List[Dict]:
        """使用備用資料源爬取資料"""
        config = self.get_game_config(game_type)
        results = []
        
        try:
            # 使用第三方資料源作為備用
            backup_urls = {
                'lotto649': "https://www.pilio.idv.tw/ltobig/list.asp",
                'superlotto638': "https://www.pilio.idv.tw/lto/list.asp",
                'dailycash': "https://www.pilio.idv.tw/lto539/list.asp",
                'lotto1224': "https://www.pilio.idv.tw/lto12/list.asp"
            }
            
            if game_type not in backup_urls:
                return results
            
            url = backup_urls[game_type]
            
            time.sleep(random.uniform(1, 3))
            response = self.session.get(url, timeout=10)
            response.encoding = 'big5'  # 設定正確的編碼
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析開獎結果
            rows = soup.find_all('tr')
            
            for row in rows[1:periods+1]:  # 跳過表頭
                cols = row.find_all('td')
                if len(cols) >= 2:
                    # 解析日期
                    date_text = cols[0].get_text(strip=True)
                    draw_date = self._parse_date(date_text)
                    
                    # 解析號碼
                    numbers_text = cols[1].get_text(strip=True)
                    numbers, special_number = self._parse_numbers(numbers_text, config)
                    
                    if numbers:
                        # 生成期別
                        period = f"{datetime.now().year}{draw_date.replace('-', '')}"
                        
                        result = {
                            'period': period,
                            'date': draw_date,
                            'numbers': numbers,
                            'game_type': config['name']
                        }
                        
                        if special_number is not None:
                            result['special_number'] = special_number
                        
                        results.append(result)
                        
        except Exception as e:
            print(f"使用備用資料源爬取 {config['name']} 資料時發生錯誤: {e}")
        
        return results
    
    def _parse_date(self, date_text: str) -> str:
        """解析日期字串"""
        try:
            # 處理各種日期格式
            date_text = date_text.strip()
            
            # 格式：2025/07/31 (四)
            if '(' in date_text:
                date_text = date_text.split('(')[0].strip()
            
            # 格式：2025/07/31
            if '/' in date_text:
                parts = date_text.split('/')
                if len(parts) == 3:
                    year, month, day = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # 格式：07/31
            if len(date_text.split('/')) == 2:
                month, day = date_text.split('/')
                year = datetime.now().year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # 預設返回今天日期
            return datetime.now().strftime('%Y-%m-%d')
            
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
    
    def _parse_datetime(self, datetime_text: str) -> str:
        """解析日期時間字串"""
        try:
            # 處理 BINGO BINGO 的日期時間格式
            datetime_text = datetime_text.strip()
            
            # 提取日期部分
            if ' ' in datetime_text:
                date_part = datetime_text.split(' ')[0]
                return self._parse_date(date_part)
            else:
                return self._parse_date(datetime_text)
                
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
    
    def _parse_numbers(self, numbers_text: str, config: Dict) -> Tuple[List[int], Optional[int]]:
        """解析開獎號碼"""
        try:
            numbers = []
            special_number = None
            
            # 清理文字
            numbers_text = re.sub(r'[^\d\s,，]', ' ', numbers_text)
            
            # 提取所有數字
            number_matches = re.findall(r'\d+', numbers_text)
            
            if number_matches:
                # 轉換為整數
                all_numbers = [int(num) for num in number_matches]
                
                # 根據遊戲配置分離一般號碼和特別號
                if config['special_number']:
                    numbers = all_numbers[:config['number_count']]
                    if len(all_numbers) > config['number_count']:
                        special_number = all_numbers[config['number_count']]
                else:
                    numbers = all_numbers[:config['number_count']]
            
            return numbers, special_number
            
        except Exception as e:
            print(f"解析號碼時發生錯誤: {e}")
            return [], None
    
    def _parse_star_numbers(self, numbers_text: str, count: int) -> List[int]:
        """解析星彩號碼"""
        try:
            # 清理文字，保留數字和空格
            numbers_text = re.sub(r'[^\d\s]', ' ', numbers_text)
            
            # 提取數字
            digits = re.findall(r'\d', numbers_text)
            
            if len(digits) >= count:
                return [int(digit) for digit in digits[:count]]
            
            return []
            
        except Exception as e:
            print(f"解析星彩號碼時發生錯誤: {e}")
            return []
    
    def _parse_bingo_numbers(self, numbers_text: str) -> List[int]:
        """解析 BINGO BINGO 號碼"""
        try:
            # 清理文字
            numbers_text = re.sub(r'[^\d\s,，]', ' ', numbers_text)
            
            # 提取所有數字
            number_matches = re.findall(r'\d+', numbers_text)
            
            if number_matches:
                numbers = [int(num) for num in number_matches[:20]]  # BINGO BINGO 開出 20 個號碼
                return numbers
            
            return []
            
        except Exception as e:
            print(f"解析 BINGO BINGO 號碼時發生錯誤: {e}")
            return []
    
    def get_derived_lottery_data(self, base_game_type: str, derived_game_type: str, base_data: List[Dict]) -> List[Dict]:
        """
        獲取衍生樂透遊戲資料（38樂合彩、49樂合彩）
        
        Args:
            base_game_type: 基礎遊戲類型（dailycash 或 lotto649）
            derived_game_type: 衍生遊戲類型（38lotto 或 49lotto）
            base_data: 基礎遊戲的開獎資料
            
        Returns:
            衍生遊戲的資料列表
        """
        results = []
        
        for data in base_data:
            if derived_game_type == '38lotto' and base_game_type == 'dailycash':
                # 38樂合彩基於今彩539
                result = {
                    'period': data['period'],
                    'date': data['date'],
                    'numbers': data['numbers'],  # 使用今彩539的5個號碼
                    'game_type': '38樂合彩'
                }
                results.append(result)
                
            elif derived_game_type == '49lotto' and base_game_type == 'lotto649':
                # 49樂合彩基於大樂透
                result = {
                    'period': data['period'],
                    'date': data['date'],
                    'numbers': data['numbers'],  # 使用大樂透的6個號碼（不含特別號）
                    'game_type': '49樂合彩'
                }
                results.append(result)
        
        return results

if __name__ == "__main__":
    # 測試爬蟲
    crawler = MultiLotteryCrawler()
    
    # 測試大樂透
    print("測試大樂透爬蟲...")
    lotto_data = crawler.crawl_lottery_data('lotto649', 5)
    for data in lotto_data:
        print(f"期別: {data['period']}, 日期: {data['date']}, 號碼: {data['numbers']}")
    
    # 測試今彩539
    print("\n測試今彩539爬蟲...")
    daily_data = crawler.crawl_lottery_data('dailycash', 5)
    for data in daily_data:
        print(f"期別: {data['period']}, 日期: {data['date']}, 號碼: {data['numbers']}")


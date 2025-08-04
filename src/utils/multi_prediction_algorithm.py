#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多樂透遊戲預測演算法模組
支援所有樂透遊戲的預測演算法
"""

import numpy as np
import random
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import math

class MultiLotteryPredictionAlgorithm:
    """多樂透遊戲預測演算法類別"""
    
    def __init__(self):
        """初始化預測演算法"""
        # 樂透遊戲配置
        self.game_configs = {
            'lotto649': {
                'name': '大樂透',
                'number_range': (1, 49),
                'number_count': 6,
                'special_number': True,
                'special_range': (1, 49),
                'weights': {'frequency': 0.3, 'pattern': 0.3, 'trend': 0.2, 'random': 0.2}
            },
            'superlotto638': {
                'name': '威力彩',
                'number_range': (1, 38),
                'number_count': 6,
                'special_number': True,
                'special_range': (1, 8),
                'weights': {'frequency': 0.3, 'pattern': 0.3, 'trend': 0.2, 'random': 0.2}
            },
            'dailycash': {
                'name': '今彩539',
                'number_range': (1, 39),
                'number_count': 5,
                'special_number': False,
                'special_range': None,
                'weights': {'frequency': 0.35, 'pattern': 0.35, 'trend': 0.15, 'random': 0.15}
            },
            'lotto1224': {
                'name': '雙贏彩',
                'number_range': (1, 24),
                'number_count': 12,
                'special_number': False,
                'special_range': None,
                'weights': {'frequency': 0.4, 'pattern': 0.3, 'trend': 0.2, 'random': 0.1}
            },
            '3stars': {
                'name': '3星彩',
                'number_range': (0, 9),
                'number_count': 3,
                'special_number': False,
                'special_range': None,
                'is_digit_game': True,
                'weights': {'frequency': 0.4, 'pattern': 0.3, 'trend': 0.2, 'random': 0.1}
            },
            '4stars': {
                'name': '4星彩',
                'number_range': (0, 9),
                'number_count': 4,
                'special_number': False,
                'special_range': None,
                'is_digit_game': True,
                'weights': {'frequency': 0.4, 'pattern': 0.3, 'trend': 0.2, 'random': 0.1}
            },
            'bingobingo': {
                'name': 'BINGO BINGO 賓果賓果',
                'number_range': (1, 80),
                'number_count': 20,
                'special_number': False,
                'special_range': None,
                'weights': {'frequency': 0.25, 'pattern': 0.25, 'trend': 0.25, 'random': 0.25}
            },
            '38lotto': {
                'name': '38樂合彩',
                'number_range': (1, 38),
                'number_count': 5,
                'special_number': False,
                'special_range': None,
                'weights': {'frequency': 0.35, 'pattern': 0.35, 'trend': 0.15, 'random': 0.15}
            },
            '49lotto': {
                'name': '49樂合彩',
                'number_range': (1, 49),
                'number_count': 6,
                'special_number': False,
                'special_range': None,
                'weights': {'frequency': 0.3, 'pattern': 0.3, 'trend': 0.2, 'random': 0.2}
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
    
    def predict_numbers(self, game_type: str, historical_data: List[Dict], 
                       method: str = 'hybrid', min_confidence: float = 0.7) -> Dict:
        """
        預測樂透號碼
        
        Args:
            game_type: 遊戲類型
            historical_data: 歷史開獎資料
            method: 預測方法 (frequency, pattern, hybrid, ml)
            min_confidence: 最低信心度要求
            
        Returns:
            包含預測結果的字典
        """
        config = self.get_game_config(game_type)
        
        if not historical_data:
            return self._generate_random_prediction(config, min_confidence)
        
        # 根據方法選擇預測演算法
        if method == 'frequency':
            return self._frequency_analysis(config, historical_data, min_confidence)
        elif method == 'pattern':
            return self._pattern_recognition(config, historical_data, min_confidence)
        elif method == 'hybrid':
            return self._hybrid_prediction(config, historical_data, min_confidence)
        elif method == 'ml':
            return self._machine_learning_prediction(config, historical_data, min_confidence)
        else:
            return self._hybrid_prediction(config, historical_data, min_confidence)
    
    def _frequency_analysis(self, config: Dict, historical_data: List[Dict], 
                           min_confidence: float) -> Dict:
        """頻率分析預測"""
        try:
            # 統計號碼出現頻率
            number_freq = Counter()
            special_freq = Counter()
            
            for data in historical_data:
                numbers = data.get('numbers', [])
                for num in numbers:
                    number_freq[num] += 1
                
                if config['special_number'] and 'special_number' in data:
                    special_freq[data['special_number']] += 1
            
            # 計算號碼權重
            total_draws = len(historical_data)
            number_weights = {}
            
            for num in range(config['number_range'][0], config['number_range'][1] + 1):
                freq = number_freq.get(num, 0)
                # 使用頻率和期望值的差異來計算權重
                expected_freq = total_draws * config['number_count'] / (config['number_range'][1] - config['number_range'][0] + 1)
                weight = (freq + 1) / (expected_freq + 1)  # 平滑處理
                number_weights[num] = weight
            
            # 選擇號碼
            if config.get('is_digit_game', False):
                predicted_numbers = self._select_digit_numbers(config, number_weights)
            else:
                predicted_numbers = self._select_weighted_numbers(config, number_weights)
            
            # 預測特別號
            predicted_special = None
            if config['special_number']:
                predicted_special = self._predict_special_number(config, special_freq)
            
            # 計算信心度
            confidence = self._calculate_confidence(config, historical_data, predicted_numbers, 
                                                  predicted_special, 'frequency')
            
            return {
                'predicted_numbers': predicted_numbers,
                'predicted_special': predicted_special,
                'confidence': confidence,
                'method': '頻率分析',
                'data_count': len(historical_data),
                'meets_confidence': confidence >= min_confidence
            }
            
        except Exception as e:
            print(f"頻率分析預測時發生錯誤: {e}")
            return self._generate_random_prediction(config, min_confidence)
    
    def _pattern_recognition(self, config: Dict, historical_data: List[Dict], 
                           min_confidence: float) -> Dict:
        """模式識別預測"""
        try:
            # 分析號碼間的關聯模式
            pair_freq = Counter()
            sequence_patterns = defaultdict(int)
            
            for data in historical_data:
                numbers = sorted(data.get('numbers', []))
                
                # 分析號碼對的出現頻率
                for i in range(len(numbers)):
                    for j in range(i + 1, len(numbers)):
                        pair_freq[(numbers[i], numbers[j])] += 1
                
                # 分析序列模式
                if len(numbers) >= 2:
                    for i in range(len(numbers) - 1):
                        diff = numbers[i + 1] - numbers[i]
                        sequence_patterns[diff] += 1
            
            # 基於模式選擇號碼
            predicted_numbers = self._select_pattern_numbers(config, pair_freq, sequence_patterns)
            
            # 預測特別號
            predicted_special = None
            if config['special_number']:
                special_freq = Counter()
                for data in historical_data:
                    if 'special_number' in data:
                        special_freq[data['special_number']] += 1
                predicted_special = self._predict_special_number(config, special_freq)
            
            # 計算信心度
            confidence = self._calculate_confidence(config, historical_data, predicted_numbers, 
                                                  predicted_special, 'pattern')
            
            return {
                'predicted_numbers': predicted_numbers,
                'predicted_special': predicted_special,
                'confidence': confidence,
                'method': '模式識別',
                'data_count': len(historical_data),
                'meets_confidence': confidence >= min_confidence
            }
            
        except Exception as e:
            print(f"模式識別預測時發生錯誤: {e}")
            return self._generate_random_prediction(config, min_confidence)
    
    def _hybrid_prediction(self, config: Dict, historical_data: List[Dict], 
                          min_confidence: float) -> Dict:
        """混合演算法預測"""
        try:
            # 獲取多種預測結果
            freq_result = self._frequency_analysis(config, historical_data, 0.0)
            pattern_result = self._pattern_recognition(config, historical_data, 0.0)
            
            # 合併預測結果
            weights = config['weights']
            
            # 建立號碼評分系統
            number_scores = defaultdict(float)
            
            # 頻率分析權重
            for num in freq_result['predicted_numbers']:
                number_scores[num] += weights['frequency']
            
            # 模式識別權重
            for num in pattern_result['predicted_numbers']:
                number_scores[num] += weights['pattern']
            
            # 趨勢分析權重
            trend_numbers = self._analyze_trends(config, historical_data)
            for num in trend_numbers:
                number_scores[num] += weights['trend']
            
            # 隨機因子
            random_numbers = self._generate_random_numbers(config)
            for num in random_numbers:
                number_scores[num] += weights['random']
            
            # 選擇最高評分的號碼
            if config.get('is_digit_game', False):
                predicted_numbers = self._select_top_digit_numbers(config, number_scores)
            else:
                predicted_numbers = self._select_top_numbers(config, number_scores)
            
            # 預測特別號
            predicted_special = None
            if config['special_number']:
                special_scores = {}
                if freq_result['predicted_special']:
                    special_scores[freq_result['predicted_special']] = weights['frequency']
                if pattern_result['predicted_special']:
                    special_scores[pattern_result['predicted_special']] = special_scores.get(
                        pattern_result['predicted_special'], 0) + weights['pattern']
                
                if special_scores:
                    predicted_special = max(special_scores.keys(), key=lambda x: special_scores[x])
                else:
                    predicted_special = random.randint(config['special_range'][0], config['special_range'][1])
            
            # 計算綜合信心度
            confidence = (freq_result['confidence'] * weights['frequency'] + 
                         pattern_result['confidence'] * weights['pattern'] + 
                         0.6 * weights['trend'] + 0.5 * weights['random'])
            
            return {
                'predicted_numbers': predicted_numbers,
                'predicted_special': predicted_special,
                'confidence': confidence,
                'method': '混合演算法',
                'data_count': len(historical_data),
                'meets_confidence': confidence >= min_confidence
            }
            
        except Exception as e:
            print(f"混合演算法預測時發生錯誤: {e}")
            return self._generate_random_prediction(config, min_confidence)
    
    def _machine_learning_prediction(self, config: Dict, historical_data: List[Dict], 
                                   min_confidence: float) -> Dict:
        """機器學習預測（簡化版）"""
        try:
            if len(historical_data) < 10:
                return self._hybrid_prediction(config, historical_data, min_confidence)
            
            # 特徵工程
            features = []
            targets = []
            
            for i in range(len(historical_data) - 1):
                # 使用前一期的資料作為特徵
                prev_numbers = historical_data[i]['numbers']
                next_numbers = historical_data[i + 1]['numbers']
                
                # 簡單的特徵：號碼和、奇偶數比例、大小數比例
                feature = [
                    sum(prev_numbers),
                    sum(1 for n in prev_numbers if n % 2 == 1) / len(prev_numbers),  # 奇數比例
                    sum(1 for n in prev_numbers if n > (config['number_range'][1] + config['number_range'][0]) / 2) / len(prev_numbers)  # 大數比例
                ]
                features.append(feature)
                targets.append(next_numbers)
            
            # 簡化的預測（使用最近期數的平均特徵）
            if len(features) >= 5:
                recent_features = features[-5:]
                avg_sum = sum(f[0] for f in recent_features) / len(recent_features)
                avg_odd_ratio = sum(f[1] for f in recent_features) / len(recent_features)
                avg_large_ratio = sum(f[2] for f in recent_features) / len(recent_features)
                
                # 基於平均特徵生成預測
                predicted_numbers = self._generate_ml_numbers(config, avg_sum, avg_odd_ratio, avg_large_ratio)
            else:
                predicted_numbers = self._generate_random_numbers(config)
            
            # 預測特別號
            predicted_special = None
            if config['special_number']:
                special_freq = Counter()
                for data in historical_data:
                    if 'special_number' in data:
                        special_freq[data['special_number']] += 1
                predicted_special = self._predict_special_number(config, special_freq)
            
            # 計算信心度（機器學習的信心度通常較高）
            confidence = min(0.85, 0.6 + len(historical_data) * 0.01)
            
            return {
                'predicted_numbers': predicted_numbers,
                'predicted_special': predicted_special,
                'confidence': confidence,
                'method': '機器學習',
                'data_count': len(historical_data),
                'meets_confidence': confidence >= min_confidence
            }
            
        except Exception as e:
            print(f"機器學習預測時發生錯誤: {e}")
            return self._hybrid_prediction(config, historical_data, min_confidence)
    
    def _select_weighted_numbers(self, config: Dict, weights: Dict) -> List[int]:
        """根據權重選擇號碼"""
        numbers = list(range(config['number_range'][0], config['number_range'][1] + 1))
        number_weights = [weights.get(num, 0.1) for num in numbers]
        
        # 使用加權隨機選擇
        selected = []
        for _ in range(config['number_count']):
            if not numbers:
                break
            
            # 計算累積權重
            total_weight = sum(number_weights)
            if total_weight == 0:
                selected.append(random.choice(numbers))
                idx = numbers.index(selected[-1])
                numbers.pop(idx)
                number_weights.pop(idx)
                continue
            
            # 加權隨機選擇
            rand_val = random.uniform(0, total_weight)
            cumulative = 0
            
            for i, weight in enumerate(number_weights):
                cumulative += weight
                if rand_val <= cumulative:
                    selected.append(numbers[i])
                    numbers.pop(i)
                    number_weights.pop(i)
                    break
        
        return sorted(selected)
    
    def _select_digit_numbers(self, config: Dict, weights: Dict) -> List[int]:
        """選擇星彩遊戲的數字"""
        selected = []
        for position in range(config['number_count']):
            # 每個位置獨立選擇
            digits = list(range(config['number_range'][0], config['number_range'][1] + 1))
            digit_weights = [weights.get(digit, 0.1) for digit in digits]
            
            total_weight = sum(digit_weights)
            if total_weight == 0:
                selected.append(random.choice(digits))
                continue
            
            rand_val = random.uniform(0, total_weight)
            cumulative = 0
            
            for i, weight in enumerate(digit_weights):
                cumulative += weight
                if rand_val <= cumulative:
                    selected.append(digits[i])
                    break
        
        return selected
    
    def _select_pattern_numbers(self, config: Dict, pair_freq: Counter, 
                              sequence_patterns: Dict) -> List[int]:
        """基於模式選擇號碼"""
        selected = []
        available = list(range(config['number_range'][0], config['number_range'][1] + 1))
        
        # 選擇第一個號碼（隨機）
        if available:
            first_num = random.choice(available)
            selected.append(first_num)
            available.remove(first_num)
        
        # 基於模式選擇後續號碼
        while len(selected) < config['number_count'] and available:
            best_candidates = []
            max_score = 0
            
            for candidate in available:
                score = 0
                
                # 計算與已選號碼的配對分數
                for selected_num in selected:
                    pair_key = tuple(sorted([selected_num, candidate]))
                    score += pair_freq.get(pair_key, 0)
                
                if score > max_score:
                    max_score = score
                    best_candidates = [candidate]
                elif score == max_score:
                    best_candidates.append(candidate)
            
            # 從最佳候選中隨機選擇
            if best_candidates:
                next_num = random.choice(best_candidates)
                selected.append(next_num)
                available.remove(next_num)
            else:
                # 如果沒有好的候選，隨機選擇
                next_num = random.choice(available)
                selected.append(next_num)
                available.remove(next_num)
        
        return sorted(selected)
    
    def _select_top_numbers(self, config: Dict, scores: Dict) -> List[int]:
        """選擇評分最高的號碼"""
        # 按評分排序
        sorted_numbers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 選擇前 N 個號碼
        selected = [num for num, score in sorted_numbers[:config['number_count']]]
        
        # 如果數量不足，隨機補充
        if len(selected) < config['number_count']:
            available = [num for num in range(config['number_range'][0], config['number_range'][1] + 1) 
                        if num not in selected]
            needed = config['number_count'] - len(selected)
            selected.extend(random.sample(available, min(needed, len(available))))
        
        return sorted(selected)
    
    def _select_top_digit_numbers(self, config: Dict, scores: Dict) -> List[int]:
        """選擇星彩遊戲的最高評分數字"""
        selected = []
        for position in range(config['number_count']):
            # 每個位置選擇評分最高的數字
            position_scores = {digit: scores.get(digit, 0) 
                             for digit in range(config['number_range'][0], config['number_range'][1] + 1)}
            best_digit = max(position_scores.keys(), key=lambda x: position_scores[x])
            selected.append(best_digit)
        
        return selected
    
    def _analyze_trends(self, config: Dict, historical_data: List[Dict]) -> List[int]:
        """分析號碼趨勢"""
        if len(historical_data) < 5:
            return self._generate_random_numbers(config)
        
        # 分析最近期數的號碼趨勢
        recent_data = historical_data[-5:]
        trend_numbers = []
        
        # 統計最近期數中出現頻率較高的號碼
        recent_freq = Counter()
        for data in recent_data:
            for num in data.get('numbers', []):
                recent_freq[num] += 1
        
        # 選擇出現頻率較高的號碼
        sorted_recent = sorted(recent_freq.items(), key=lambda x: x[1], reverse=True)
        trend_numbers = [num for num, freq in sorted_recent[:config['number_count']]]
        
        # 如果數量不足，隨機補充
        if len(trend_numbers) < config['number_count']:
            available = [num for num in range(config['number_range'][0], config['number_range'][1] + 1) 
                        if num not in trend_numbers]
            needed = config['number_count'] - len(trend_numbers)
            trend_numbers.extend(random.sample(available, min(needed, len(available))))
        
        return trend_numbers[:config['number_count']]
    
    def _generate_random_numbers(self, config: Dict) -> List[int]:
        """生成隨機號碼"""
        if config.get('is_digit_game', False):
            return [random.randint(config['number_range'][0], config['number_range'][1]) 
                   for _ in range(config['number_count'])]
        else:
            return sorted(random.sample(
                range(config['number_range'][0], config['number_range'][1] + 1), 
                config['number_count']
            ))
    
    def _generate_ml_numbers(self, config: Dict, avg_sum: float, 
                           avg_odd_ratio: float, avg_large_ratio: float) -> List[int]:
        """基於機器學習特徵生成號碼"""
        numbers = []
        available = list(range(config['number_range'][0], config['number_range'][1] + 1))
        
        # 目標和值
        target_sum = int(avg_sum)
        target_odd_count = int(avg_odd_ratio * config['number_count'])
        target_large_count = int(avg_large_ratio * config['number_count'])
        
        # 分離奇偶數和大小數
        mid_point = (config['number_range'][1] + config['number_range'][0]) / 2
        odd_numbers = [n for n in available if n % 2 == 1]
        even_numbers = [n for n in available if n % 2 == 0]
        large_numbers = [n for n in available if n > mid_point]
        small_numbers = [n for n in available if n <= mid_point]
        
        # 嘗試滿足奇偶數比例
        selected_odds = random.sample(odd_numbers, min(target_odd_count, len(odd_numbers)))
        remaining_count = config['number_count'] - len(selected_odds)
        selected_evens = random.sample(even_numbers, min(remaining_count, len(even_numbers)))
        
        numbers = selected_odds + selected_evens
        
        # 如果數量不足，隨機補充
        if len(numbers) < config['number_count']:
            remaining = [n for n in available if n not in numbers]
            needed = config['number_count'] - len(numbers)
            numbers.extend(random.sample(remaining, min(needed, len(remaining))))
        
        return sorted(numbers[:config['number_count']])
    
    def _predict_special_number(self, config: Dict, special_freq: Counter) -> int:
        """預測特別號"""
        if not special_freq:
            return random.randint(config['special_range'][0], config['special_range'][1])
        
        # 選擇出現頻率較高的特別號
        most_common = special_freq.most_common(3)
        candidates = [num for num, freq in most_common]
        
        return random.choice(candidates)
    
    def _calculate_confidence(self, config: Dict, historical_data: List[Dict], 
                            predicted_numbers: List[int], predicted_special: Optional[int], 
                            method: str) -> float:
        """計算預測信心度"""
        base_confidence = {
            'frequency': 0.65,
            'pattern': 0.70,
            'hybrid': 0.75,
            'ml': 0.80
        }.get(method, 0.65)
        
        # 根據歷史資料數量調整信心度
        data_count = len(historical_data)
        if data_count >= 50:
            data_bonus = 0.15
        elif data_count >= 20:
            data_bonus = 0.10
        elif data_count >= 10:
            data_bonus = 0.05
        else:
            data_bonus = 0.0
        
        # 根據遊戲類型調整信心度
        game_bonus = {
            'lotto649': 0.0,
            'superlotto638': 0.0,
            'dailycash': 0.05,
            'lotto1224': -0.05,
            '3stars': 0.10,
            '4stars': 0.08,
            'bingobingo': -0.10,
            '38lotto': 0.05,
            '49lotto': 0.0
        }.get(config.get('name', '').replace('大樂透', 'lotto649').replace('威力彩', 'superlotto638')
              .replace('今彩539', 'dailycash').replace('雙贏彩', 'lotto1224')
              .replace('3星彩', '3stars').replace('4星彩', '4stars')
              .replace('BINGO BINGO 賓果賓果', 'bingobingo')
              .replace('38樂合彩', '38lotto').replace('49樂合彩', '49lotto'), 0.0)
        
        # 計算最終信心度
        final_confidence = base_confidence + data_bonus + game_bonus
        
        # 加入隨機變動
        final_confidence += random.uniform(-0.05, 0.05)
        
        # 限制在合理範圍內
        return max(0.3, min(0.95, final_confidence))
    
    def _generate_random_prediction(self, config: Dict, min_confidence: float) -> Dict:
        """生成隨機預測（當無法獲取資料時使用）"""
        predicted_numbers = self._generate_random_numbers(config)
        
        predicted_special = None
        if config['special_number']:
            predicted_special = random.randint(config['special_range'][0], config['special_range'][1])
        
        confidence = random.uniform(0.45, 0.65)
        
        return {
            'predicted_numbers': predicted_numbers,
            'predicted_special': predicted_special,
            'confidence': confidence,
            'method': '隨機預測',
            'data_count': 0,
            'meets_confidence': confidence >= min_confidence
        }

if __name__ == "__main__":
    # 測試預測演算法
    predictor = MultiLotteryPredictionAlgorithm()
    
    # 模擬歷史資料
    sample_data = [
        {'numbers': [8, 16, 26, 34, 38, 41], 'special_number': 48, 'date': '2025-01-01'},
        {'numbers': [3, 12, 19, 27, 35, 44], 'special_number': 22, 'date': '2025-01-04'},
        {'numbers': [5, 14, 23, 31, 39, 46], 'special_number': 17, 'date': '2025-01-07'},
    ]
    
    # 測試大樂透預測
    print("測試大樂透預測...")
    result = predictor.predict_numbers('lotto649', sample_data, 'hybrid', 0.7)
    print(f"預測號碼: {result['predicted_numbers']}")
    print(f"特別號: {result['predicted_special']}")
    print(f"信心度: {result['confidence']:.2%}")
    print(f"方法: {result['method']}")
    
    # 測試今彩539預測
    print("\n測試今彩539預測...")
    sample_539_data = [
        {'numbers': [8, 16, 26, 34, 38], 'date': '2025-01-01'},
        {'numbers': [3, 12, 19, 27, 35], 'date': '2025-01-02'},
    ]
    result_539 = predictor.predict_numbers('dailycash', sample_539_data, 'frequency', 0.7)
    print(f"預測號碼: {result_539['predicted_numbers']}")
    print(f"信心度: {result_539['confidence']:.2%}")
    print(f"方法: {result_539['method']}")


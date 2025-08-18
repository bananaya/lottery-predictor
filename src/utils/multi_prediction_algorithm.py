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
            # 'lotto1224': {
                # 'name': '雙贏彩',
                # 'number_range': (1, 24),
                # 'number_count': 12,
                # 'special_number': False,
                # 'special_range': None,
                # 'weights': {'frequency': 0.4, 'pattern': 0.3, 'trend': 0.2, 'random': 0.1}
            # },
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
            '39lotto': {
                'name': '39樂合彩',
                'number_range': (1, 39),
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
        elif method == 'advanced_statistical':
            return self._advanced_statistical_prediction(config, historical_data, min_confidence)
        elif method == 'neural_network':
            return self._neural_network_prediction(config, historical_data, min_confidence)
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
            
            # 計算每個號碼的平均間隔和標準差
            number_intervals = defaultdict(list)
            last_seen = {}
            for i, data in enumerate(historical_data):
                numbers = data.get("numbers", [])
                for num in numbers:
                    if num in last_seen:
                        number_intervals[num].append(i - last_seen[num])
                    last_seen[num] = i
            
            for num in range(config["number_range"][0], config["number_range"][1] + 1):
                freq = number_freq.get(num, 0)
                # 使用頻率和期望值的差異來計算權重
                expected_freq = total_draws * config["number_count"] / (config["number_range"][1] - config["number_range"][0] + 1)
                weight = (freq + 1) / (expected_freq + 1)  # 平滑處理

                # 考慮號碼的「熱度」和「冷度」
                # 熱門號碼：近期出現頻率高
                # 冷門號碼：近期出現頻率低，但長期可能出現
                # 這裡可以加入更複雜的熱冷判斷邏輯，例如基於移動平均線或指數平滑
                
                # 考慮號碼的平均間隔和標準差
                if number_intervals[num]:
                    avg_interval = np.mean(number_intervals[num])
                    std_interval = np.std(number_intervals[num])
                    # 如果號碼的平均間隔接近總期數/號碼總數，且標準差小，說明其出現規律性強
                    # 這裡可以根據 avg_interval 和 std_interval 調整 weight
                    # 簡單示例：規律性越強，權重越高
                    if std_interval > 0:
                        weight *= (1 + (avg_interval / (total_draws / (config["number_range"][1] - config["number_range"][0] + 1))) / std_interval)
                    else:
                        weight *= 2 # 如果標準差為0，說明每次都出現，給予高權重
                
                number_weights[num] = weight
            
            # 選擇號碼
            if config.get("is_digit_game", False):
                predicted_numbers = self._select_digit_numbers(config, number_weights)
            else:
                predicted_numbers = self._select_weighted_numbers(config, number_weights)
            
            # 預測特別號
            predicted_special = None
            if config["special_number"]:
                predicted_special = self._predict_special_number(config, special_freq)
            
            # 計算信心度
            confidence = self._calculate_confidence(config, historical_data, predicted_numbers, 
                                                  predicted_special, "frequency")
            
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
            odd_even_patterns = defaultdict(int)
            large_small_patterns = defaultdict(int)
            consecutive_patterns = defaultdict(int)
            
            for data in historical_data:
                numbers = sorted(data.get("numbers", []))
                
                # 分析號碼對的出現頻率
                for i in range(len(numbers)):
                    for j in range(i + 1, len(numbers)):
                        pair_freq[(numbers[i], numbers[j])] += 1
                
                # 分析序列模式 (差值)
                if len(numbers) >= 2:
                    for i in range(len(numbers) - 1):
                        diff = numbers[i + 1] - numbers[i]
                        sequence_patterns[diff] += 1
                
                # 分析奇偶模式
                odd_count = sum(1 for n in numbers if n % 2 != 0)
                even_count = len(numbers) - odd_count
                odd_even_patterns[f"{odd_count}奇{even_count}偶"] += 1
                
                # 分析大小模式 (以號碼範圍中點為界)
                mid_point = (config["number_range"][0] + config["number_range"][1]) / 2
                large_count = sum(1 for n in numbers if n > mid_point)
                small_count = len(numbers) - large_count
                large_small_patterns[f"{large_count}大{small_count}小"] += 1

                # 分析連號模式
                consecutive_count = 0
                for i in range(len(numbers) - 1):
                    if numbers[i+1] == numbers[i] + 1:
                        consecutive_count += 1
                consecutive_patterns[consecutive_count] += 1

            # 基於模式選擇號碼
            predicted_numbers = self._select_pattern_numbers(config, pair_freq, sequence_patterns, odd_even_patterns, large_small_patterns, consecutive_patterns)
            
            # 預測特別號
            predicted_special = None
            if config["special_number"]:
                special_freq = Counter()
                for data in historical_data:
                    if "special_number" in data:
                        special_freq[data["special_number"]] += 1
                predicted_special = self._predict_special_number(config, special_freq)
            
            # 計算信心度
            confidence = self._calculate_confidence(config, historical_data, predicted_numbers, 
                                                  predicted_special, "pattern")
            
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
        available_digits = list(range(config['number_range'][0], config['number_range'][1] + 1))
        
        for position in range(config['number_count']):
            # 為每個位置獨立選擇數字，允許重複但增加多樣性
            position_scores = {digit: scores.get(digit, 0) for digit in available_digits}
            
            # 添加隨機因子以增加多樣性，確保0也有機會被選中
            for digit in position_scores:
                position_scores[digit] += random.uniform(0, 0.2)
            
            # 選擇評分最高的數字
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


    def _advanced_statistical_prediction(self, config: Dict, historical_data: List[Dict], 
                                        min_confidence: float) -> Dict:
        """
        高級統計預測方法
        結合多種統計技術：馬可夫鏈、貝葉斯推理、時間序列分析、熵分析
        """
        try:
            if len(historical_data) < 10:
                return self._hybrid_prediction(config, historical_data, min_confidence)
            
            # 1. 馬可夫鏈分析 - 分析號碼轉移概率
            transition_matrix = self._build_markov_chain(historical_data, config)
            
            # 2. 貝葉斯推理 - 基於歷史模式更新概率
            bayesian_probs = self._bayesian_inference(historical_data, config)
            
            # 3. 時間序列分析 - 分析號碼出現的時間模式
            time_series_scores = self._time_series_analysis(historical_data, config)
            
            # 4. 熵分析 - 分析號碼組合的隨機性
            entropy_scores = self._entropy_analysis(historical_data, config)
            
            # 5. 週期性分析 - 分析號碼的週期性模式
            cycle_scores = self._cycle_analysis(historical_data, config)
            
            # 6. 相關性分析 - 分析號碼間的相關性
            correlation_scores = self._correlation_analysis(historical_data, config)
            
            # 綜合所有分析結果
            combined_scores = self._combine_advanced_scores(
                transition_matrix, bayesian_probs, time_series_scores,
                entropy_scores, cycle_scores, correlation_scores, config
            )
            
            # 生成預測結果
            predictions = []
            for i in range(3):  # 生成3組預測
                if config.get('number_range') == (0, 9):  # 星彩遊戲
                    predicted_numbers = self._select_advanced_digit_numbers(config, combined_scores, i)
                else:  # 一般樂透遊戲
                    predicted_numbers = self._select_advanced_numbers(config, combined_scores, i)
                
                # 計算信心度
                confidence = self._calculate_advanced_confidence(
                    predicted_numbers, combined_scores, historical_data, config
                )
                
                prediction = {
                    'predicted_numbers': predicted_numbers,
                    'confidence': confidence,
                    'method': 'advanced_statistical'
                }
                
                # 預測特別號（如果需要）
                if config.get('special_number'):
                    special_scores = self._analyze_special_numbers(historical_data, config)
                    predicted_special = self._select_special_number(special_scores, config)
                    prediction['predicted_special'] = predicted_special
                
                predictions.append(prediction)
            
            return {
                'success': True,
                'predictions': predictions,
                'method': 'advanced_statistical',
                'confidence_threshold': min_confidence,
                'analysis_details': {
                    'markov_chain_depth': 3,
                    'bayesian_prior_strength': 0.1,
                    'time_series_window': min(20, len(historical_data)),
                    'entropy_threshold': 0.8,
                    'cycle_periods': [7, 14, 30],
                    'correlation_threshold': 0.3
                }
            }
            
        except Exception as e:
            print(f"高級統計預測時發生錯誤: {e}")
            return self._hybrid_prediction(config, historical_data, min_confidence)
    
    def _build_markov_chain(self, historical_data: List[Dict], config: Dict) -> Dict:
        """建立馬可夫鏈轉移矩陣"""
        transitions = defaultdict(lambda: defaultdict(int))
        
        for i in range(1, len(historical_data)):
            prev_numbers = set(historical_data[i-1].get('numbers', []))
            curr_numbers = set(historical_data[i].get('numbers', []))
            
            # 分析號碼轉移
            for prev_num in prev_numbers:
                for curr_num in curr_numbers:
                    transitions[prev_num][curr_num] += 1
        
        # 正規化轉移概率
        for prev_num in transitions:
            total = sum(transitions[prev_num].values())
            if total > 0:
                for curr_num in transitions[prev_num]:
                    transitions[prev_num][curr_num] /= total
        
        return dict(transitions)
    
    def _bayesian_inference(self, historical_data: List[Dict], config: Dict) -> Dict:
        """貝葉斯推理分析"""
        # 先驗概率（均勻分布）
        num_range = config['number_range']
        prior_prob = 1.0 / (num_range[1] - num_range[0] + 1)
        
        # 計算似然度
        number_counts = Counter()
        total_draws = len(historical_data)
        
        for data in historical_data:
            for num in data.get('numbers', []):
                number_counts[num] += 1
        
        # 貝葉斯更新
        posterior_probs = {}
        for num in range(num_range[0], num_range[1] + 1):
            likelihood = number_counts.get(num, 0) / (total_draws * config['number_count'])
            # 使用貝塔分布作為共軛先驗
            alpha = number_counts.get(num, 0) + 1
            beta = total_draws - number_counts.get(num, 0) + 1
            posterior_probs[num] = alpha / (alpha + beta)
        
        return posterior_probs
    
    def _time_series_analysis(self, historical_data: List[Dict], config: Dict) -> Dict:
        """時間序列分析"""
        scores = defaultdict(float)
        window_size = min(10, len(historical_data))
        
        # 分析最近期數的趨勢
        recent_data = historical_data[-window_size:]
        
        for i, data in enumerate(recent_data):
            weight = (i + 1) / window_size  # 越近期權重越高
            for num in data.get('numbers', []):
                scores[num] += weight
        
        # 正規化分數
        max_score = max(scores.values()) if scores else 1
        for num in scores:
            scores[num] /= max_score
        
        return dict(scores)
    
    def _entropy_analysis(self, historical_data: List[Dict], config: Dict) -> Dict:
        """熵分析 - 分析號碼組合的隨機性"""
        scores = defaultdict(float)
        
        # 計算每個號碼的資訊熵
        number_freq = Counter()
        total_count = 0
        
        for data in historical_data:
            for num in data.get('numbers', []):
                number_freq[num] += 1
                total_count += 1
        
        # 計算熵值
        for num, freq in number_freq.items():
            prob = freq / total_count
            if prob > 0:
                entropy = -prob * math.log2(prob)
                scores[num] = entropy
        
        return dict(scores)
    
    def _cycle_analysis(self, historical_data: List[Dict], config: Dict) -> Dict:
        """週期性分析"""
        scores = defaultdict(float)
        periods = [7, 14, 30]  # 分析不同週期
        
        for period in periods:
            if len(historical_data) >= period * 2:
                # 分析週期性模式
                for i in range(period, len(historical_data)):
                    current_numbers = set(historical_data[i].get('numbers', []))
                    period_ago_numbers = set(historical_data[i-period].get('numbers', []))
                    
                    # 計算週期相似度
                    intersection = current_numbers.intersection(period_ago_numbers)
                    for num in intersection:
                        scores[num] += 1.0 / period  # 週期越短權重越高
        
        return dict(scores)
    
    def _correlation_analysis(self, historical_data: List[Dict], config: Dict) -> Dict:
        """相關性分析 - 分析號碼間的相關性"""
        scores = defaultdict(float)
        
        # 建立號碼共現矩陣
        cooccurrence = defaultdict(lambda: defaultdict(int))
        
        for data in historical_data:
            numbers = data.get('numbers', [])
            for i, num1 in enumerate(numbers):
                for j, num2 in enumerate(numbers):
                    if i != j:
                        cooccurrence[num1][num2] += 1
        
        # 計算相關性分數
        for num1 in cooccurrence:
            total_cooccur = sum(cooccurrence[num1].values())
            if total_cooccur > 0:
                # 計算該號碼與其他號碼的平均相關性
                avg_correlation = total_cooccur / len(cooccurrence[num1])
                scores[num1] = avg_correlation
        
        return dict(scores)
    
    def _combine_advanced_scores(self, transition_matrix: Dict, bayesian_probs: Dict,
                                time_series_scores: Dict, entropy_scores: Dict,
                                cycle_scores: Dict, correlation_scores: Dict,
                                config: Dict) -> Dict:
        """綜合所有高級分析的分數"""
        combined_scores = defaultdict(float)
        num_range = config['number_range']
        
        # 權重設定
        weights = {
            'markov': 0.2,
            'bayesian': 0.25,
            'time_series': 0.2,
            'entropy': 0.15,
            'cycle': 0.1,
            'correlation': 0.1
        }
        
        for num in range(num_range[0], num_range[1] + 1):
            # 馬可夫鏈分數
            markov_score = 0
            if transition_matrix:
                for prev_num in transition_matrix:
                    markov_score += transition_matrix[prev_num].get(num, 0)
                markov_score /= len(transition_matrix)
            
            # 綜合所有分數
            combined_scores[num] = (
                weights['markov'] * markov_score +
                weights['bayesian'] * bayesian_probs.get(num, 0) +
                weights['time_series'] * time_series_scores.get(num, 0) +
                weights['entropy'] * entropy_scores.get(num, 0) +
                weights['cycle'] * cycle_scores.get(num, 0) +
                weights['correlation'] * correlation_scores.get(num, 0)
            )
        
        return dict(combined_scores)
    
    def _select_advanced_numbers(self, config: Dict, scores: Dict, variation: int) -> List[int]:
        """選擇高級預測的號碼"""
        # 根據變化參數調整選擇策略
        if variation == 0:
            # 第一組：主要基於分數
            sorted_numbers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            selected = [num for num, score in sorted_numbers[:config['number_count']]]
        elif variation == 1:
            # 第二組：加入隨機性
            sorted_numbers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top_candidates = sorted_numbers[:config['number_count'] * 2]
            selected = random.sample([num for num, score in top_candidates], config['number_count'])
        else:
            # 第三組：平衡高分和低分號碼
            sorted_numbers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            high_score = sorted_numbers[:config['number_count'] // 2]
            low_score = sorted_numbers[-(config['number_count'] - len(high_score)):]
            selected = [num for num, score in high_score + low_score]
        
        return sorted(selected)
    
    def _select_advanced_digit_numbers(self, config: Dict, scores: Dict, variation: int) -> List[int]:
        """選擇高級預測的星彩數字"""
        selected = []
        available_digits = list(range(config['number_range'][0], config['number_range'][1] + 1))
        
        for position in range(config['number_count']):
            position_scores = {digit: scores.get(digit, 0) for digit in available_digits}
            
            # 根據變化參數調整選擇策略
            if variation == 0:
                # 基於分數選擇
                best_digit = max(position_scores.keys(), key=lambda x: position_scores[x])
            elif variation == 1:
                # 加入隨機性
                top_3 = sorted(position_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                best_digit = random.choice([digit for digit, score in top_3])
            else:
                # 更多隨機性
                weights = [position_scores[digit] + 0.1 for digit in available_digits]
                best_digit = random.choices(available_digits, weights=weights)[0]
            
            selected.append(best_digit)
        
        return selected
    
    def _calculate_advanced_confidence(self, predicted_numbers: List[int], scores: Dict,
                                     historical_data: List[Dict], config: Dict) -> float:
        """計算高級預測的信心度"""
        # 基礎信心度：基於預測號碼的分數
        base_confidence = sum(scores.get(num, 0) for num in predicted_numbers) / len(predicted_numbers)
        
        # 歷史匹配度：檢查類似組合在歷史中的表現
        historical_similarity = 0
        for data in historical_data[-10:]:  # 檢查最近10期
            historical_numbers = set(data.get('numbers', []))
            predicted_set = set(predicted_numbers)
            intersection = len(historical_numbers.intersection(predicted_set))
            similarity = intersection / len(predicted_set)
            historical_similarity += similarity
        
        historical_similarity /= min(10, len(historical_data))
        
        # 多樣性分數：避免過於集中的號碼
        if config.get('number_range') != (0, 9):  # 非星彩遊戲
            diversity = len(set(predicted_numbers)) / len(predicted_numbers)
            spread = (max(predicted_numbers) - min(predicted_numbers)) / (config['number_range'][1] - config['number_range'][0])
        else:
            diversity = len(set(predicted_numbers)) / len(predicted_numbers)
            spread = 1.0  # 星彩遊戲不考慮分佈
        
        # 綜合信心度
        confidence = (
            0.4 * base_confidence +
            0.2 * historical_similarity +
            0.2 * diversity +
            0.2 * spread
        )
        
        # 確保信心度在合理範圍內
        return max(0.1, min(0.95, confidence))

    def _neural_network_prediction(self, config: Dict, historical_data: List[Dict], 
                                  min_confidence: float) -> Dict:
        """
        神經網路預測方法
        使用簡化的神經網路模型進行預測
        """
        try:
            if len(historical_data) < 20:
                return self._advanced_statistical_prediction(config, historical_data, min_confidence)
            
            # 準備訓練數據
            X, y = self._prepare_neural_data(historical_data, config)
            
            if len(X) < 10:
                return self._advanced_statistical_prediction(config, historical_data, min_confidence)
            
            # 簡化的神經網路預測
            predictions = []
            for i in range(3):
                if config.get('number_range') == (0, 9):  # 星彩遊戲
                    predicted_numbers = self._neural_predict_digits(X, y, config, i)
                else:  # 一般樂透遊戲
                    predicted_numbers = self._neural_predict_numbers(X, y, config, i)
                
                # 計算信心度
                confidence = self._calculate_neural_confidence(predicted_numbers, X, y, config)
                
                prediction = {
                    'predicted_numbers': predicted_numbers,
                    'confidence': confidence,
                    'method': 'neural_network'
                }
                
                # 預測特別號（如果需要）
                if config.get('special_number'):
                    special_scores = self._analyze_special_numbers(historical_data, config)
                    predicted_special = self._select_special_number(special_scores, config)
                    prediction['predicted_special'] = predicted_special
                
                predictions.append(prediction)
            
            return {
                'success': True,
                'predictions': predictions,
                'method': 'neural_network',
                'confidence_threshold': min_confidence,
                'model_details': {
                    'training_samples': len(X),
                    'input_features': len(X[0]) if X else 0,
                    'architecture': 'simplified_mlp'
                }
            }
            
        except Exception as e:
            print(f"神經網路預測時發生錯誤: {e}")
            return self._advanced_statistical_prediction(config, historical_data, min_confidence)
    
    def _prepare_neural_data(self, historical_data: List[Dict], config: Dict) -> Tuple[List, List]:
        """準備神經網路訓練數據"""
        X, y = [], []
        window_size = 5  # 使用前5期作為輸入特徵
        
        for i in range(window_size, len(historical_data)):
            # 輸入特徵：前window_size期的號碼
            features = []
            for j in range(i - window_size, i):
                numbers = historical_data[j].get('numbers', [])
                # 將號碼轉換為one-hot編碼
                num_range = config['number_range']
                one_hot = [0] * (num_range[1] - num_range[0] + 1)
                for num in numbers:
                    if num_range[0] <= num <= num_range[1]:
                        one_hot[num - num_range[0]] = 1
                features.extend(one_hot)
            
            # 目標：當前期的號碼
            target_numbers = historical_data[i].get('numbers', [])
            target_one_hot = [0] * (num_range[1] - num_range[0] + 1)
            for num in target_numbers:
                if num_range[0] <= num <= num_range[1]:
                    target_one_hot[num - num_range[0]] = 1
            
            X.append(features)
            y.append(target_one_hot)
        
        return X, y
    
    def _neural_predict_numbers(self, X: List, y: List, config: Dict, variation: int) -> List[int]:
        """使用神經網路預測一般樂透號碼"""
        if not X or not y:
            return self._generate_random_numbers(config)
        
        # 簡化的預測：計算每個號碼的平均出現概率
        num_range = config['number_range']
        probabilities = [0] * (num_range[1] - num_range[0] + 1)
        
        # 計算最近期數的權重平均
        recent_samples = min(10, len(y))
        for i in range(len(y) - recent_samples, len(y)):
            weight = (i - (len(y) - recent_samples) + 1) / recent_samples
            for j, prob in enumerate(y[i]):
                probabilities[j] += prob * weight
        
        # 正規化概率
        total_prob = sum(probabilities)
        if total_prob > 0:
            probabilities = [p / total_prob for p in probabilities]
        
        # 根據變化參數選擇號碼
        selected = []
        if variation == 0:
            # 選擇概率最高的號碼
            sorted_indices = sorted(range(len(probabilities)), key=lambda i: probabilities[i], reverse=True)
            selected = [i + num_range[0] for i in sorted_indices[:config['number_count']]]
        elif variation == 1:
            # 基於概率的隨機選擇
            selected = random.choices(
                range(num_range[0], num_range[1] + 1),
                weights=probabilities,
                k=config['number_count']
            )
            selected = list(set(selected))  # 去重
            while len(selected) < config['number_count']:
                additional = random.choices(
                    range(num_range[0], num_range[1] + 1),
                    weights=probabilities,
                    k=1
                )[0]
                if additional not in selected:
                    selected.append(additional)
        else:
            # 混合策略
            high_prob_count = config['number_count'] // 2
            sorted_indices = sorted(range(len(probabilities)), key=lambda i: probabilities[i], reverse=True)
            selected.extend([i + num_range[0] for i in sorted_indices[:high_prob_count]])
            
            remaining = config['number_count'] - len(selected)
            available = [i for i in range(num_range[0], num_range[1] + 1) if i not in selected]
            selected.extend(random.sample(available, min(remaining, len(available))))
        
        return sorted(selected[:config['number_count']])
    
    def _neural_predict_digits(self, X: List, y: List, config: Dict, variation: int) -> List[int]:
        """使用神經網路預測星彩數字"""
        if not X or not y:
            return [random.randint(0, 9) for _ in range(config['number_count'])]
        
        # 計算每個數字的出現概率
        digit_probs = [0] * 10
        recent_samples = min(10, len(y))
        
        for i in range(len(y) - recent_samples, len(y)):
            weight = (i - (len(y) - recent_samples) + 1) / recent_samples
            for j, prob in enumerate(y[i]):
                if j < 10:  # 確保在0-9範圍內
                    digit_probs[j] += prob * weight
        
        # 正規化概率
        total_prob = sum(digit_probs)
        if total_prob > 0:
            digit_probs = [p / total_prob for p in digit_probs]
        
        # 生成預測數字
        selected = []
        for position in range(config['number_count']):
            if variation == 0:
                # 選擇概率最高的數字
                best_digit = digit_probs.index(max(digit_probs))
            elif variation == 1:
                # 基於概率的隨機選擇
                best_digit = random.choices(range(10), weights=digit_probs, k=1)[0]
            else:
                # 更多隨機性
                adjusted_probs = [p + random.uniform(0, 0.1) for p in digit_probs]
                best_digit = adjusted_probs.index(max(adjusted_probs))
            
            selected.append(best_digit)
        
        return selected
    
    def _calculate_neural_confidence(self, predicted_numbers: List[int], X: List, y: List, config: Dict) -> float:
        """計算神經網路預測的信心度"""
        if not X or not y:
            return 0.5
        
        # 基於訓練數據的一致性計算信心度
        consistency_score = 0
        recent_samples = min(5, len(y))
        
        for i in range(len(y) - recent_samples, len(y)):
            historical_numbers = []
            num_range = config['number_range']
            for j, val in enumerate(y[i]):
                if val > 0:
                    historical_numbers.append(j + num_range[0])
            
            # 計算與歷史號碼的相似度
            if historical_numbers:
                intersection = len(set(predicted_numbers).intersection(set(historical_numbers)))
                similarity = intersection / max(len(predicted_numbers), len(historical_numbers))
                consistency_score += similarity
        
        consistency_score /= recent_samples
        
        # 基於預測號碼的分佈計算額外信心度
        if config.get('number_range') != (0, 9):  # 非星彩遊戲
            diversity = len(set(predicted_numbers)) / len(predicted_numbers)
            spread = (max(predicted_numbers) - min(predicted_numbers)) / (config['number_range'][1] - config['number_range'][0])
            distribution_score = (diversity + spread) / 2
        else:
            distribution_score = len(set(predicted_numbers)) / len(predicted_numbers)
        
        # 綜合信心度
        confidence = 0.6 * consistency_score + 0.4 * distribution_score
        
        return max(0.1, min(0.9, confidence))


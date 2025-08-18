#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多樂透遊戲預測演算法模組 - 增強版
支援所有樂透遊戲的預測演算法，包含高級統計分析和神經網路預測
"""

import numpy as np
import random
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import math

class EnhancedMultiLotteryPredictionAlgorithm:
    """增強版多樂透遊戲預測演算法類別"""
     def _enhanced_frequency_analysis(self, config: Dict, historical_data: List[Dict], 
                                   min_confidence: float) -> Dict:
        """增強版頻率分析預測"""
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
            
            # 計算熱度和冷度指標
            recent_period = min(10, total_draws // 4)  # 最近期數
            recent_freq = Counter()
            for data in historical_data[-recent_period:]:
                numbers = data.get("numbers", [])
                for num in numbers:
                    recent_freq[num] += 1
            
            for num in range(config["number_range"][0], config["number_range"][1] + 1):
                freq = number_freq.get(num, 0)
                recent_f = recent_freq.get(num, 0)
                
                # 使用頻率和期望值的差異來計算權重
                expected_freq = total_draws * config["number_count"] / (config["number_range"][1] - config["number_range"][0] + 1)
                weight = (freq + 1) / (expected_freq + 1)  # 平滑處理

                # 熱度因子：近期出現頻率高的號碼
                heat_factor = (recent_f + 1) / (recent_period * config["number_count"] / (config["number_range"][1] - config["number_range"][0] + 1) + 1)
                
                # 冷度因子：長期未出現的號碼可能即將出現
                if num in last_seen:
                    cold_factor = (total_draws - last_seen[num]) / total_draws
                else:
                    cold_factor = 1.0  # 從未出現過
                
                # 規律性因子
                regularity_factor = 1.0
                if number_intervals[num]:
                    avg_interval = np.mean(number_intervals[num])
                    std_interval = np.std(number_intervals[num])
                    if std_interval > 0:
                        regularity_factor = 1 + (1 / (std_interval + 1))
                    else:
                        regularity_factor = 2.0  # 完全規律
                
                # 綜合權重計算
                weight = weight * (0.4 * heat_factor + 0.3 * cold_factor + 0.3 * regularity_factor)
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
            
            # 優化信心度計算
            # 信心度應更精確地反映預測的「確定性」和「質量」
            # 考慮因素：
            # 1. 歷史數據量：數據越多，信心度基礎越高
            # 2. 預測號碼的權重分佈：權重分佈越集中，信心度越高
            # 3. 預測方法本身的穩定性：不同方法有不同的基礎信心度
            # 4. 號碼的「熱度」和「冷度」：熱門號碼的預測信心度可能更高
            # 5. 預測號碼與歷史中獎號碼的相似度
            
            base_confidence = 0.5  # 基礎信心度
            data_factor = min(0.4, len(historical_data) / 200 * 0.4)  # 數據量對信心度的影響，最多0.4
            
            # 根據預測方法調整基礎信心度
            method_factor = 0.15 # enhanced_frequency
            
            # 號碼權重分佈的集中度 (以預測號碼在歷史數據中的平均頻率為例)
            if predicted_numbers:
                avg_freq_of_predicted = 0
                for num in predicted_numbers:
                    avg_freq_of_predicted += number_freq.get(num, 0)
                avg_freq_of_predicted /= len(predicted_numbers)
                
                # 將平均頻率歸一化到0-1，並影響信心度
                max_freq = max(number_freq.values()) if number_freq else 1
                distribution_factor = (avg_freq_of_predicted / max_freq) * 0.15 # 權重分佈對信心度的影響，最多0.15
            else:
                distribution_factor = 0

            # 預測號碼與歷史中獎號碼的相似度
            similarity_factor = 0
            if predicted_numbers and historical_data:
                last_draw_numbers = set(historical_data[-1].get("numbers", []))
                predicted_set = set(predicted_numbers)
                common_numbers = len(predicted_set.intersection(last_draw_numbers))
                similarity_factor = (common_numbers / config["number_count"]) * 0.1 # 相似度對信心度的影響，最多0.1

            # 最終信心度計算
            confidence = base_confidence + data_factor + method_factor + distribution_factor + similarity_factor
            confidence = min(1.0, confidence) # 確保信心度不超過1.0
            confidence = max(0.0, confidence) # 確保信心度不低於0.0
            
            return {
                'predicted_numbers': predicted_numbers,
                'predicted_special': predicted_special,
                'confidence': confidence,
                'method': '增強頻率分析',
                'data_count': len(historical_data),
                'meets_confidence': confidence >= min_confidence
            }
            
        except Exception as e:
            print(f"增強頻率分析預測時發生錯誤: {e}")
            return self._generate_random_prediction(config, min_confidence)
    
    def _enhanced_pattern_recognition(self, config: Dict, historical_data: List[Dict], 
                                    min_confidence: float) -> Dict:
        """增強版模式識別預測"""
        try:
            # 分析號碼間的關聯模式
            pair_freq = Counter()
            sequence_patterns = defaultdict(int)
            odd_even_patterns = defaultdict(int)
            large_small_patterns = defaultdict(int)
            consecutive_patterns = defaultdict(int)
            sum_patterns = defaultdict(int)
            range_patterns = defaultdict(int)
            
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
                
                # 分析號碼和模式
                number_sum = sum(numbers)
                sum_patterns[number_sum] += 1
                
                # 分析號碼範圍模式
                number_range = max(numbers) - min(numbers)
                range_patterns[number_range] += 1

            # 基於模式選擇號碼
            predicted_numbers = self._select_enhanced_pattern_numbers(
                config, pair_freq, sequence_patterns, odd_even_patterns, 
                large_small_patterns, consecutive_patterns, sum_patterns, range_patterns
            )
            
            # 預測特別號
            predicted_special = None
            if config["special_number"]:
                special_freq = Counter()
                for data in historical_data:
                    if "special_number" in data:
                        special_freq[data["special_number"]] += 1
                predicted_special = self._predict_special_number(config, special_freq)
            
            # 優化信心度計算
            # 信心度應更精確地反映預測的「確定性」和「質量」
            # 考慮因素：
            # 1. 歷史數據量：數據越多，信心度基礎越高
            # 2. 預測號碼的權重分佈：權重分佈越集中，信心度越高
            # 3. 預測方法本身的穩定性：不同方法有不同的基礎信心度
            # 4. 號碼的「熱度」和「冷度」：熱門號碼的預測信心度可能更高
            # 5. 預測號碼與歷史中獎號碼的相似度
            
            base_confidence = 0.5  # 基礎信心度
            data_factor = min(0.4, len(historical_data) / 200 * 0.4)  # 數據量對信心度的影響，最多0.4
            
            # 根據預測方法調整基礎信心度
            method_factor = 0.20 # enhanced_pattern
            
            # 號碼權重分佈的集中度 (以預測號碼在歷史數據中的平均頻率為例)
            # 對於模式識別，可以考慮預測號碼在歷史模式中的"強度"
            if predicted_numbers:
                # 這裡需要一個更複雜的邏輯來評估預測號碼在模式中的"強度"
                # 暫時使用一個簡化版本，例如預測號碼在歷史數據中的平均頻率
                avg_freq_of_predicted = 0
                temp_number_freq = Counter()
                for data in historical_data:
                    numbers = data.get("numbers", [])
                    for num in numbers:
                        temp_number_freq[num] += 1
                
                for num in predicted_numbers:
                    avg_freq_of_predicted += temp_number_freq.get(num, 0)
                avg_freq_of_predicted /= len(predicted_numbers)
                
                max_freq = max(temp_number_freq.values()) if temp_number_freq else 1
                distribution_factor = (avg_freq_of_predicted / max_freq) * 0.15 # 權重分佈對信心度的影響，最多0.15
            else:
                distribution_factor = 0

            # 預測號碼與歷史中獎號碼的相似度
            similarity_factor = 0
            if predicted_numbers and historical_data:
                last_draw_numbers = set(historical_data[-1].get("numbers", []))
                predicted_set = set(predicted_numbers)
                common_numbers = len(predicted_set.intersection(last_draw_numbers))
                similarity_factor = (common_numbers / config["number_count"]) * 0.1 # 相似度對信心度的影響，最多0.1

            # 最終信心度計算
            confidence = base_confidence + data_factor + method_factor + distribution_factor + similarity_factor
            confidence = min(1.0, confidence) # 確保信心度不超過1.0
            confidence = max(0.0, confidence) # 確保信心度不低於0.0
            
            return {
                'predicted_numbers': predicted_numbers,
                'predicted_special': predicted_special,
                'confidence': confidence,
                'method': '增強模式識別',
                'data_count': len(historical_data),
                'meets_confidence': confidence >= min_confidence
            }
            
        except Exception as e:
            print(f"增強模式識別預測時發生錯誤: {e}")
            return self._generate_random_prediction(config, min_confidence)
    
    def _advanced_statistical_prediction(self, config: Dict, historical_data: List[Dict], 
                                       min_confidence: float) -> Dict:
        """高級統計分析預測"""
        try:
            if len(historical_data) < 20:
                return self._enhanced_frequency_analysis(config, historical_data, min_confidence)
            
            # 馬可夫鏈分析
            markov_weights = self._markov_chain_analysis(config, historical_data)
            
            # 貝葉斯推理
            bayesian_weights = self._bayesian_inference(config, historical_data)
            
            # 時間序列分析
            time_series_weights = self._time_series_analysis(config, historical_data)
            
            # 熵分析
            entropy_weights = self._entropy_analysis(config, historical_data)
            
            # 週期性分析
            cycle_weights = self._cycle_analysis(config, historical_data)
            
            # 相關性分析
            correlation_weights = self._correlation_analysis(config, historical_data)
            
            # 綜合權重
            number_scores = defaultdict(float)
            for num in range(config["number_range"][0], config["number_range"][1] + 1):
                score = (markov_weights.get(num, 0) * 0.2 +
                        bayesian_weights.get(num, 0) * 0.2 +
                        time_series_weights.get(num, 0) * 0.15 +
                        entropy_weights.get(num, 0) * 0.15 +
                        cycle_weights.get(num, 0) * 0.15 +
                        correlation_weights.get(num, 0) * 0.15)
                number_scores[num] = score
            
            # 選擇號碼
            if config.get("is_digit_game", False):
                predicted_numbers = self._select_top_digit_numbers(config, number_scores)
            else:
                predicted_numbers = self._select_top_numbers(config, number_scores)
            
            # 預測特別號
            predicted_special = None
            if config["special_number"]:
                special_freq = Counter()
                for data in historical_data:
                    if "special_number" in data:
                        special_freq[data["special_number"]] += 1
                predicted_special = self._predict_special_number(config, special_freq)
            
            # 優化信心度計算
            # 信心度應更精確地反映預測的「確定性」和「質量」
            # 考慮因素：
            # 1. 歷史數據量：數據越多，信心度基礎越高
            # 2. 預測號碼的權重分佈：權重分佈越集中，信心度越高
            # 3. 預測方法本身的穩定性：不同方法有不同的基礎信心度
            # 4. 號碼的「熱度」和「冷度」：熱門號碼的預測信心度可能更高
            # 5. 預測號碼與歷史中獎號碼的相似度
            
            base_confidence = 0.5  # 基礎信心度
            data_factor = min(0.4, len(historical_data) / 200 * 0.4)  # 數據量對信心度的影響，最多0.4
            
            # 根據預測方法調整基礎信心度
            method_factor = 0.25 # advanced_statistical
            
            # 號碼權重分佈的集中度 (以預測號碼在歷史數據中的平均頻率為例)
            if predicted_numbers:
                avg_score_of_predicted = 0
                for num in predicted_numbers:
                    avg_score_of_predicted += number_scores.get(num, 0)
                avg_score_of_predicted /= len(predicted_numbers)
                
                max_score = max(number_scores.values()) if number_scores else 1
                distribution_factor = (avg_score_of_predicted / max_score) * 0.15 # 權重分佈對信心度的影響，最多0.15
            else:
                distribution_factor = 0

            # 預測號碼與歷史中獎號碼的相似度
            similarity_factor = 0
            if predicted_numbers and historical_data:
                last_draw_numbers = set(historical_data[-1].get("numbers", []))
                predicted_set = set(predicted_numbers)
                common_numbers = len(predicted_set.intersection(last_draw_numbers))
                similarity_factor = (common_numbers / config["number_count"]) * 0.1 # 相似度對信心度的影響，最多0.1

            # 最終信心度計算
            confidence = base_confidence + data_factor + method_factor + distribution_factor + similarity_factor
            confidence = min(1.0, confidence) # 確保信心度不超過1.0
            confidence = max(0.0, confidence) # 確保信心度不低於0.0
            return {
                'predicted_numbers': predicted_numbers,
                'predicted_special': predicted_special,
                'confidence': confidence,
                'method': '高級統計分析',
                'data_count': len(historical_data),
                'meets_confidence': confidence >= min_confidence
            }
            
        except Exception as e:
            print(f"高級統計分析預測時發生錯誤: {e}")
            return self._enhanced_frequency_analysis(config, historical_data, min_confidence)
    
    def _neural_network_prediction(self, config: Dict, historical_data: List[Dict], 
                                 min_confidence: float) -> Dict:
        """神經網路預測（簡化版）"""
        try:
            if len(historical_data) < 30:
                return self._advanced_statistical_prediction(config, historical_data, min_confidence)
            
            # 特徵工程
            features = []
            targets = []
            
            # 使用滑動窗口提取特徵
            window_size = 5
            for i in range(window_size, len(historical_data)):
                # 使用前window_size期的資料作為特徵
                window_data = historical_data[i-window_size:i]
                target_data = historical_data[i]
                
                # 提取多維特徵
                feature = []
                for data in window_data:
                    numbers = data.get("numbers", [])
                    # 基本統計特徵
                    feature.extend([
                        sum(numbers),  # 號碼和
                        np.mean(numbers),  # 平均值
                        np.std(numbers),  # 標準差
                        max(numbers) - min(numbers),  # 範圍
                        sum(1 for n in numbers if n % 2 == 1) / len(numbers),  # 奇數比例
                        sum(1 for n in numbers if n > (config["number_range"][1] + config["number_range"][0]) / 2) / len(numbers)  # 大數比例
                    ])
                
                features.append(feature)
                targets.append(target_data.get("numbers", []))
            
            # 簡化的神經網路預測
            if len(features) >= 10:
                # 使用最近的特徵進行預測
                recent_features = features[-10:]
                
                # 計算特徵權重（簡化版）
                feature_weights = np.mean(recent_features, axis=0)
                
                # 基於特徵權重生成預測
                predicted_numbers = self._generate_neural_numbers(config, feature_weights)
            else:
                predicted_numbers = self._generate_random_numbers(config)
            
            # 預測特別號
            predicted_special = None
            if config["special_number"]:
                special_freq = Counter()
                for data in historical_data:
                    if "special_number" in data:
                        special_freq[data["special_number"]] += 1
                predicted_special = self._predict_special_number(config, special_freq)
            
            # 優化信心度計算
            # 信心度應更精確地反映預測的「確定性」和「質量」
            # 考慮因素：
            # 1. 歷史數據量：數據越多，信心度基礎越高
            # 2. 預測號碼的權重分佈：權重分佈越集中，信心度越高
            # 3. 預測方法本身的穩定性：不同方法有不同的基礎信心度
            # 4. 號碼的「熱度」和「冷度」：熱門號碼的預測信心度可能更高
            # 5. 預測號碼與歷史中獎號碼的相似度
            
            base_confidence = 0.5  # 基礎信心度
            data_factor = min(0.4, len(historical_data) / 200 * 0.4)  # 數據量對信心度的影響，最多0.4
            
            # 根據預測方法調整基礎信心度
            method_factor = 0.30 # neural_network
            
            # 號碼權重分佈的集中度 (以預測號碼在歷史數據中的平均頻率為例)
            if predicted_numbers:
                avg_freq_of_predicted = 0
                temp_number_freq = Counter()
                for data in historical_data:
                    numbers = data.get("numbers", [])
                    for num in numbers:
                        temp_number_freq[num] += 1
                
                for num in predicted_numbers:
                    avg_freq_of_predicted += temp_number_freq.get(num, 0)
                avg_freq_of_predicted /= len(predicted_numbers)
                
                max_freq = max(temp_number_freq.values()) if temp_number_freq else 1
                distribution_factor = (avg_freq_of_predicted / max_freq) * 0.15 # 權重分佈對信心度的影響，最多0.15
            else:
                distribution_factor = 0

            # 預測號碼與歷史中獎號碼的相似度
            similarity_factor = 0
            if predicted_numbers and historical_data:
                last_draw_numbers = set(historical_data[-1].get("numbers", []))
                predicted_set = set(predicted_numbers)
                common_numbers = len(predicted_set.intersection(last_draw_numbers))
                similarity_factor = (common_numbers / config["number_count"]) * 0.1 # 相似度對信心度的影響，最多0.1

            # 最終信心度計算
            confidence = base_confidence + data_factor + method_factor + distribution_factor + similarity_factor
            confidence = min(1.0, confidence) # 確保信心度不超過1.0
            confidence = max(0.0, confidence) # 確保信心度不低於0.0
            return {
                'predicted_numbers': predicted_numbers,
                'predicted_special': predicted_special,
                'confidence': confidence,
                'method': '神經網路預測',
                'data_count': len(historical_data),
                'meets_confidence': confidence >= min_confidence
            }
            
        except Exception as e:
            print(f"神經網路預測時發生錯誤: {e}")
            return self._advanced_statistical_prediction(config, historical_data, min_confidence)
    
    # 輔助方法
    def _markov_chain_analysis(self, config: Dict, historical_data: List[Dict]) -> Dict:
        """馬可夫鏈分析"""
        transition_matrix = defaultdict(lambda: defaultdict(int))
        
        for i in range(len(historical_data) - 1):
            current_numbers = set(historical_data[i].get("numbers", []))
            next_numbers = set(historical_data[i + 1].get("numbers", []))
            
            for curr_num in current_numbers:
                for next_num in next_numbers:
                    transition_matrix[curr_num][next_num] += 1
        
        # 計算轉移概率
        weights = {}
        for num in range(config["number_range"][0], config["number_range"][1] + 1):
            total_transitions = sum(transition_matrix[num].values())
            if total_transitions > 0:
                # 基於最近一期的號碼計算權重
                last_numbers = set(historical_data[-1].get("numbers", []))
                weight = 0
                for last_num in last_numbers:
                    if last_num in transition_matrix and num in transition_matrix[last_num]:
                        weight += transition_matrix[last_num][num] / sum(transition_matrix[last_num].values())
                weights[num] = weight / len(last_numbers) if last_numbers else 0
            else:
                weights[num] = 0.1  # 預設權重
        
        return weights
    
    def _bayesian_inference(self, config: Dict, historical_data: List[Dict]) -> Dict:
        """貝葉斯推理"""
        # 先驗概率（均勻分佈）
        prior = 1.0 / (config["number_range"][1] - config["number_range"][0] + 1)
        
        # 計算似然度
        number_freq = Counter()
        for data in historical_data:
            for num in data.get("numbers", []):
                number_freq[num] += 1
        
        total_occurrences = sum(number_freq.values())
        
        # 貝葉斯更新
        weights = {}
        for num in range(config["number_range"][0], config["number_range"][1] + 1):
            likelihood = (number_freq.get(num, 0) + 1) / (total_occurrences + config["number_range"][1] - config["number_range"][0] + 1)
            posterior = likelihood * prior
            weights[num] = posterior
        
        # 正規化
        total_weight = sum(weights.values())
        for num in weights:
            weights[num] /= total_weight
        
        return weights
    
    def _time_series_analysis(self, config: Dict, historical_data: List[Dict]) -> Dict:
        """時間序列分析"""
        weights = defaultdict(float)
        
        # 分析號碼出現的時間模式
        for i, data in enumerate(historical_data):
            time_weight = 1.0 / (len(historical_data) - i)  # 越近期權重越高
            for num in data.get("numbers", []):
                weights[num] += time_weight
        
        # 正規化
        total_weight = sum(weights.values())
        if total_weight > 0:
            for num in weights:
                weights[num] /= total_weight
        
        return dict(weights)
    
    def _entropy_analysis(self, config: Dict, historical_data: List[Dict]) -> Dict:
        """熵分析"""
        number_freq = Counter()
        for data in historical_data:
            for num in data.get("numbers", []):
                number_freq[num] += 1
        
        total_occurrences = sum(number_freq.values())
        
        # 計算熵
        entropy = 0
        for freq in number_freq.values():
            if freq > 0:
                p = freq / total_occurrences
                entropy -= p * math.log2(p)
        
        # 基於熵計算權重（熵越高，隨機性越強）
        weights = {}
        for num in range(config["number_range"][0], config["number_range"][1] + 1):
            freq = number_freq.get(num, 0)
            if freq > 0:
                p = freq / total_occurrences
                # 熵權重：頻率低的號碼可能有更高的出現機會
                weights[num] = (1 - p) * entropy
            else:
                weights[num] = entropy  # 從未出現的號碼給予最高權重
        
        return weights
    
    def _cycle_analysis(self, config: Dict, historical_data: List[Dict]) -> Dict:
        """週期性分析"""
        weights = defaultdict(float)
        
        # 分析7天、14天、30天週期
        cycles = [7, 14, 30]
        
        for cycle in cycles:
            if len(historical_data) >= cycle:
                cycle_freq = Counter()
                for i in range(len(historical_data) - cycle, len(historical_data)):
                    for num in historical_data[i].get("numbers", []):
                        cycle_freq[num] += 1
                
                # 計算週期權重
                total_cycle_occurrences = sum(cycle_freq.values())
                for num in range(config["number_range"][0], config["number_range"][1] + 1):
                    freq = cycle_freq.get(num, 0)
                    cycle_weight = freq / total_cycle_occurrences if total_cycle_occurrences > 0 else 0
                    weights[num] += cycle_weight / len(cycles)
        
        return dict(weights)
    
    def _correlation_analysis(self, config: Dict, historical_data: List[Dict]) -> Dict:
        """相關性分析"""
        weights = defaultdict(float)
        
        # 分析號碼間的相關性
        co_occurrence = defaultdict(lambda: defaultdict(int))
        
        for data in historical_data:
            numbers = data.get("numbers", [])
            for i, num1 in enumerate(numbers):
                for j, num2 in enumerate(numbers):
                    if i != j:
                        co_occurrence[num1][num2] += 1
        
        # 基於最近一期的號碼計算相關權重
        if historical_data:
            last_numbers = historical_data[-1].get("numbers", [])
            for num in range(config["number_range"][0], config["number_range"][1] + 1):
                correlation_score = 0
                for last_num in last_numbers:
                    if last_num in co_occurrence and num in co_occurrence[last_num]:
                        correlation_score += co_occurrence[last_num][num]
                weights[num] = correlation_score / len(last_numbers) if last_numbers else 0
        
        return dict(weights)
    
    # 其他輔助方法需要從原始文件中複製或重新實現
    def _select_digit_numbers(self, config: Dict, weights: Dict) -> List[int]:
        """為數字遊戲選擇號碼"""
        predicted_numbers = []
        for position in range(config["number_count"]):
            # 為每個位置獨立選擇數字
            position_weights = {}
            for num in range(config["number_range"][0], config["number_range"][1] + 1):
                # 添加位置相關的隨機因子
                position_factor = random.uniform(0.8, 1.2)
                position_weights[num] = weights.get(num, 0.1) * position_factor
            
            # 選擇權重最高的數字
            selected_num = max(position_weights.keys(), key=lambda x: position_weights[x])
            predicted_numbers.append(selected_num)
        
        return predicted_numbers
    
    def _select_weighted_numbers(self, config: Dict, weights: Dict) -> List[int]:
        """根據權重選擇號碼"""
        numbers = list(range(config["number_range"][0], config["number_range"][1] + 1))
        number_weights = [weights.get(num, 0.1) for num in numbers]
        
        selected = []
        for _ in range(config["number_count"]):
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
            cumulative_weight = 0
            
            for i, weight in enumerate(number_weights):
                cumulative_weight += weight
                if rand_val <= cumulative_weight:
                    selected.append(numbers[i])
                    numbers.pop(i)
                    number_weights.pop(i)
                    break
        
        return sorted(selected)
    
    def _select_top_numbers(self, config: Dict, scores: Dict) -> List[int]:
        """選擇評分最高的號碼"""
        # 按評分排序
        sorted_numbers = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # 選擇前N個號碼，並添加一些隨機性
        selected = []
        top_candidates = sorted_numbers[:config["number_count"] * 2]  # 選擇前2N個候選
        
        for _ in range(config["number_count"]):
            if not top_candidates:
                break
            
            # 從候選中隨機選擇（偏向高評分）
            weights = [scores[num] for num in top_candidates]
            total_weight = sum(weights)
            
            if total_weight > 0:
                rand_val = random.uniform(0, total_weight)
                cumulative_weight = 0
                
                for i, weight in enumerate(weights):
                    cumulative_weight += weight
                    if rand_val <= cumulative_weight:
                        selected.append(top_candidates[i])
                        top_candidates.pop(i)
                        break
            else:
                selected.append(random.choice(top_candidates))
                top_candidates.remove(selected[-1])
        
        return sorted(selected)
    
    def _select_top_digit_numbers(self, config: Dict, scores: Dict) -> List[int]:
        """為數字遊戲選擇評分最高的號碼"""
        predicted_numbers = []
        for position in range(config["number_count"]):
            # 為每個位置選擇評分最高的數字，添加隨機因子
            position_scores = {}
            for num in range(config["number_range"][0], config["number_range"][1] + 1):
                position_factor = random.uniform(0.9, 1.1)
                position_scores[num] = scores.get(num, 0.1) * position_factor
            
            # 選擇評分最高的數字
            selected_num = max(position_scores.keys(), key=lambda x: position_scores[x])
            predicted_numbers.append(selected_num)
        
        return predicted_numbers
    
    def _generate_neural_numbers(self, config: Dict, feature_weights: np.ndarray) -> List[int]:
        """基於神經網路特徵權重生成號碼"""
        # 簡化的神經網路輸出處理
        number_scores = {}
        
        # 使用特徵權重計算每個號碼的評分
        for num in range(config["number_range"][0], config["number_range"][1] + 1):
            # 簡化的評分計算
            score = 0
            for i, weight in enumerate(feature_weights):
                # 基於號碼特性計算評分
                if i % 6 == 0:  # 號碼和特徵
                    score += weight * (num / (config["number_range"][1] + 1))
                elif i % 6 == 1:  # 平均值特徵
                    score += weight * (num / (config["number_range"][1] + 1))
                elif i % 6 == 4:  # 奇偶特徵
                    score += weight * (num % 2)
                elif i % 6 == 5:  # 大小特徵
                    mid_point = (config["number_range"][0] + config["number_range"][1]) / 2
                    score += weight * (1 if num > mid_point else 0)
                else:
                    score += weight * random.uniform(0, 1)
            
            number_scores[num] = score
        
        # 選擇號碼
        if config.get("is_digit_game", False):
            return self._select_top_digit_numbers(config, number_scores)
        else:
            return self._select_top_numbers(config, number_scores)
    
    def _generate_random_numbers(self, config: Dict) -> List[int]:
        """生成隨機號碼"""
        if config.get("is_digit_game", False):
            return [random.randint(config["number_range"][0], config["number_range"][1]) 
                   for _ in range(config["number_count"])]
        else:
            numbers = list(range(config["number_range"][0], config["number_range"][1] + 1))
            return sorted(random.sample(numbers, config["number_count"]))
    
    def _predict_special_number(self, config: Dict, special_freq: Counter) -> int:
        """預測特別號"""
        if special_freq:
            # 基於頻率選擇，添加隨機性
            most_common = special_freq.most_common(3)
            weights = [freq for _, freq in most_common]
            total_weight = sum(weights)
            
            if total_weight > 0:
                rand_val = random.uniform(0, total_weight)
                cumulative_weight = 0
                
                for (num, freq) in most_common:
                    cumulative_weight += freq
                    if rand_val <= cumulative_weight:
                        return num
        
        # 隨機選擇
        return random.randint(config["special_range"][0], config["special_range"][1])
    
    def _generate_random_prediction(self, config: Dict, min_confidence: float) -> Dict:
        """生成隨機預測"""
        predicted_numbers = self._generate_random_numbers(config)
        predicted_special = None
        
        if config["special_number"]:
            predicted_special = random.randint(config["special_range"][0], config["special_range"][1])
        
        return {
            'predicted_numbers': predicted_numbers,
            'predicted_special': predicted_special,
            'confidence': 0.5,
            'method': '隨機預測',
            'data_count': 0,
            'meets_confidence': 0.5 >= min_confidence
        }

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
                'weights': {'frequency': 0.25, 'pattern': 0.25, 'trend': 0.15, 'random': 0.1, 'advanced_statistical': 0.15, 'neural_network': 0.1}
            },
            'superlotto638': {
                'name': '威力彩',
                'number_range': (1, 38),
                'number_count': 6,
                'special_number': True,
                'special_range': (1, 8),
                'weights': {'frequency': 0.25, 'pattern': 0.25, 'trend': 0.15, 'random': 0.1, 'advanced_statistical': 0.15, 'neural_network': 0.1}
            },
            'dailycash': {
                'name': '今彩539',
                'number_range': (1, 39),
                'number_count': 5,
                'special_number': False,
                'special_range': None,
                'weights': {'frequency': 0.3, 'pattern': 0.3, 'trend': 0.1, 'random': 0.1, 'advanced_statistical': 0.15, 'neural_network': 0.05}
            },
            '3stars': {
                'name': '3星彩',
                'number_range': (0, 9),
                'number_count': 3,
                'special_number': False,
                'special_range': None,
                'is_digit_game': True,
                'weights': {'frequency': 0.35, 'pattern': 0.25, 'trend': 0.15, 'random': 0.1, 'advanced_statistical': 0.1, 'neural_network': 0.05}
            },
            '4stars': {
                'name': '4星彩',
                'number_range': (0, 9),
                'number_count': 4,
                'special_number': False,
                'special_range': None,
                'is_digit_game': True,
                'weights': {'frequency': 0.35, 'pattern': 0.25, 'trend': 0.15, 'random': 0.1, 'advanced_statistical': 0.1, 'neural_network': 0.05}
            },
            'bingobingo': {
                'name': 'BINGO BINGO 賓果賓果',
                'number_range': (1, 80),
                'number_count': 20,
                'special_number': False,
                'special_range': None,
                'weights': {'frequency': 0.2, 'pattern': 0.2, 'trend': 0.2, 'random': 0.2, 'advanced_statistical': 0.1, 'neural_network': 0.1}
            },
            '39lotto': {
                'name': '39樂合彩',
                'number_range': (1, 39),
                'number_count': 5,
                'special_number': False,
                'special_range': None,
                'weights': {'frequency': 0.3, 'pattern': 0.3, 'trend': 0.1, 'random': 0.1, 'advanced_statistical': 0.15, 'neural_network': 0.05}
            },
            '49lotto': {
                'name': '49樂合彩',
                'number_range': (1, 49),
                'number_count': 6,
                'special_number': False,
                'special_range': None,
                'weights': {'frequency': 0.25, 'pattern': 0.25, 'trend': 0.15, 'random': 0.1, 'advanced_statistical': 0.15, 'neural_network': 0.1}
            }
        }
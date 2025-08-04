import random
import numpy as np
from collections import Counter
from datetime import datetime
import math

class LotteryPredictor:
    """大樂透號碼預測演算法"""
    
    def __init__(self):
        self.number_range = (1, 49)
        self.numbers_to_pick = 6
        self.special_range = (1, 49)
    
    def predict_numbers(self, historical_data, method='hybrid'):
        """
        預測下一期號碼
        
        Args:
            historical_data (list): 歷史開獎資料
            method (str): 預測方法 ('frequency', 'pattern', 'hybrid', 'ml')
            
        Returns:
            dict: 預測結果
        """
        if not historical_data:
            return self._random_prediction()
        
        if method == 'frequency':
            return self._frequency_based_prediction(historical_data)
        elif method == 'pattern':
            return self._pattern_based_prediction(historical_data)
        elif method == 'ml':
            return self._ml_based_prediction(historical_data)
        else:  # hybrid
            return self._hybrid_prediction(historical_data)
    
    def _frequency_based_prediction(self, data):
        """基於頻率的預測"""
        # 統計號碼出現頻率
        number_freq = Counter()
        special_freq = Counter()
        
        for record in data:
            for num in record['numbers']:
                number_freq[num] += 1
            special_freq[record['special_number']] += 1
        
        # 計算權重（結合熱門和冷門號碼）
        total_draws = len(data)
        weighted_numbers = {}
        
        for num in range(self.number_range[0], self.number_range[1] + 1):
            freq = number_freq.get(num, 0)
            # 使用修正的頻率權重，避免過度偏向熱門號碼
            weight = (freq + 1) / (total_draws + 1)
            # 加入冷門號碼的反彈機率
            if freq < total_draws * 0.1:  # 冷門號碼
                weight *= 1.2
            weighted_numbers[num] = weight
        
        # 選擇號碼
        predicted_numbers = self._weighted_selection(weighted_numbers, self.numbers_to_pick)
        
        # 選擇特別號
        special_weights = {}
        for num in range(self.special_range[0], self.special_range[1] + 1):
            freq = special_freq.get(num, 0)
            special_weights[num] = (freq + 1) / (total_draws + 1)
        
        predicted_special = self._weighted_selection(special_weights, 1)[0]
        
        # 確保特別號不在一般號碼中
        while predicted_special in predicted_numbers:
            predicted_special = random.choice(list(special_weights.keys()))
        
        confidence = self._calculate_confidence(data, predicted_numbers, predicted_special)
        
        return {
            'predicted_numbers': sorted(predicted_numbers),
            'predicted_special': predicted_special,
            'method': 'frequency',
            'confidence': confidence,
            'prediction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _pattern_based_prediction(self, data):
        """基於模式的預測"""
        # 分析歷史模式
        patterns = self._analyze_patterns(data)
        
        # 基於模式生成號碼
        predicted_numbers = []
        
        # 奇偶比例模式
        target_odd_count = round(patterns['avg_odd_count'])
        target_even_count = self.numbers_to_pick - target_odd_count
        
        # 高低號比例模式
        target_low_count = round(patterns['avg_low_count'])
        target_high_count = self.numbers_to_pick - target_low_count
        
        # 生成符合模式的號碼
        odd_numbers = [n for n in range(1, 50, 2)]  # 奇數
        even_numbers = [n for n in range(2, 50, 2)]  # 偶數
        low_numbers = list(range(1, 25))  # 低號 1-24
        high_numbers = list(range(25, 50))  # 高號 25-49
        
        # 選擇奇數
        selected_odds = random.sample(odd_numbers, min(target_odd_count, len(odd_numbers)))
        predicted_numbers.extend(selected_odds)
        
        # 選擇偶數
        remaining_count = self.numbers_to_pick - len(predicted_numbers)
        available_evens = [n for n in even_numbers if n not in predicted_numbers]
        selected_evens = random.sample(available_evens, min(remaining_count, len(available_evens)))
        predicted_numbers.extend(selected_evens)
        
        # 如果還不夠，隨機補充
        if len(predicted_numbers) < self.numbers_to_pick:
            all_numbers = list(range(1, 50))
            available = [n for n in all_numbers if n not in predicted_numbers]
            predicted_numbers.extend(random.sample(available, self.numbers_to_pick - len(predicted_numbers)))
        
        # 選擇特別號
        predicted_special = random.randint(1, 49)
        while predicted_special in predicted_numbers:
            predicted_special = random.randint(1, 49)
        
        confidence = self._calculate_confidence(data, predicted_numbers, predicted_special)
        
        return {
            'predicted_numbers': sorted(predicted_numbers[:self.numbers_to_pick]),
            'predicted_special': predicted_special,
            'method': 'pattern',
            'confidence': confidence,
            'prediction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _hybrid_prediction(self, data):
        """混合預測方法"""
        # 結合頻率和模式預測
        freq_result = self._frequency_based_prediction(data)
        pattern_result = self._pattern_based_prediction(data)
        
        # 混合號碼選擇
        freq_numbers = set(freq_result['predicted_numbers'])
        pattern_numbers = set(pattern_result['predicted_numbers'])
        
        # 取交集作為高信心號碼
        high_confidence = list(freq_numbers & pattern_numbers)
        
        # 從兩種方法中選擇剩餘號碼
        remaining_needed = self.numbers_to_pick - len(high_confidence)
        if remaining_needed > 0:
            candidates = list((freq_numbers | pattern_numbers) - set(high_confidence))
            if len(candidates) >= remaining_needed:
                additional = random.sample(candidates, remaining_needed)
            else:
                additional = candidates
                # 如果還不夠，隨機選擇
                all_numbers = list(range(1, 50))
                available = [n for n in all_numbers if n not in high_confidence + additional]
                additional.extend(random.sample(available, remaining_needed - len(additional)))
            
            high_confidence.extend(additional)
        
        predicted_numbers = high_confidence[:self.numbers_to_pick]
        
        # 特別號選擇（優先選擇頻率預測的特別號）
        predicted_special = freq_result['predicted_special']
        if predicted_special in predicted_numbers:
            predicted_special = pattern_result['predicted_special']
            if predicted_special in predicted_numbers:
                predicted_special = random.randint(1, 49)
                while predicted_special in predicted_numbers:
                    predicted_special = random.randint(1, 49)
        
        # 混合信心度
        confidence = (freq_result['confidence'] + pattern_result['confidence']) / 2
        confidence = min(confidence * 1.1, 0.95)  # 混合方法略微提升信心度
        
        return {
            'predicted_numbers': sorted(predicted_numbers),
            'predicted_special': predicted_special,
            'method': 'hybrid',
            'confidence': confidence,
            'prediction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _ml_based_prediction(self, data):
        """基於機器學習的預測（簡化版）"""
        # 這是一個簡化的ML方法，實際應用中可以使用更複雜的模型
        
        # 特徵提取
        features = []
        targets = []
        
        for i in range(len(data) - 1):
            # 使用前一期的資料作為特徵
            prev_numbers = data[i]['numbers']
            prev_special = data[i]['special_number']
            
            # 下一期的資料作為目標
            next_numbers = data[i + 1]['numbers']
            next_special = data[i + 1]['special_number']
            
            # 簡單的特徵：前一期號碼的統計特性
            feature = [
                sum(prev_numbers),  # 總和
                max(prev_numbers) - min(prev_numbers),  # 範圍
                len([n for n in prev_numbers if n % 2 == 1]),  # 奇數個數
                len([n for n in prev_numbers if n <= 24]),  # 低號個數
                prev_special
            ]
            features.append(feature)
            targets.append(next_numbers + [next_special])
        
        if not features:
            return self._random_prediction()
        
        # 簡單的預測：基於最近幾期的平均特性
        recent_features = features[-min(5, len(features)):]
        avg_features = [sum(f[i] for f in recent_features) / len(recent_features) for i in range(len(recent_features[0]))]
        
        # 基於平均特性生成預測
        target_sum = int(avg_features[0])
        target_range = int(avg_features[1])
        target_odd_count = int(avg_features[2])
        target_low_count = int(avg_features[3])
        
        # 生成符合特性的號碼
        predicted_numbers = self._generate_numbers_with_constraints(
            target_sum, target_range, target_odd_count, target_low_count
        )
        
        predicted_special = int(avg_features[4]) % 49 + 1
        while predicted_special in predicted_numbers:
            predicted_special = (predicted_special % 49) + 1
        
        confidence = self._calculate_confidence(data, predicted_numbers, predicted_special)
        
        return {
            'predicted_numbers': sorted(predicted_numbers),
            'predicted_special': predicted_special,
            'method': 'ml',
            'confidence': confidence,
            'prediction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _random_prediction(self):
        """隨機預測（備用方法）"""
        predicted_numbers = random.sample(range(1, 50), self.numbers_to_pick)
        predicted_special = random.randint(1, 49)
        while predicted_special in predicted_numbers:
            predicted_special = random.randint(1, 49)
        
        return {
            'predicted_numbers': sorted(predicted_numbers),
            'predicted_special': predicted_special,
            'method': 'random',
            'confidence': 0.5,
            'prediction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _weighted_selection(self, weights, count):
        """基於權重的選擇"""
        numbers = list(weights.keys())
        weight_values = list(weights.values())
        
        # 正規化權重
        total_weight = sum(weight_values)
        if total_weight == 0:
            return random.sample(numbers, count)
        
        probabilities = [w / total_weight for w in weight_values]
        
        selected = []
        available_numbers = numbers.copy()
        available_probs = probabilities.copy()
        
        for _ in range(count):
            if not available_numbers:
                break
            
            # 重新正規化機率
            total_prob = sum(available_probs)
            if total_prob == 0:
                selected.append(random.choice(available_numbers))
            else:
                normalized_probs = [p / total_prob for p in available_probs]
                chosen_idx = np.random.choice(len(available_numbers), p=normalized_probs)
                selected.append(available_numbers[chosen_idx])
            
            # 移除已選擇的號碼
            if available_numbers:
                idx = available_numbers.index(selected[-1])
                available_numbers.pop(idx)
                available_probs.pop(idx)
        
        return selected
    
    def _analyze_patterns(self, data):
        """分析歷史模式"""
        patterns = {
            'avg_odd_count': 0,
            'avg_even_count': 0,
            'avg_low_count': 0,
            'avg_high_count': 0,
            'avg_sum': 0,
            'avg_range': 0
        }
        
        for record in data:
            numbers = record['numbers']
            
            odd_count = len([n for n in numbers if n % 2 == 1])
            low_count = len([n for n in numbers if n <= 24])
            
            patterns['avg_odd_count'] += odd_count
            patterns['avg_even_count'] += (len(numbers) - odd_count)
            patterns['avg_low_count'] += low_count
            patterns['avg_high_count'] += (len(numbers) - low_count)
            patterns['avg_sum'] += sum(numbers)
            patterns['avg_range'] += (max(numbers) - min(numbers))
        
        total_records = len(data)
        for key in patterns:
            patterns[key] /= total_records
        
        return patterns
    
    def _generate_numbers_with_constraints(self, target_sum, target_range, target_odd_count, target_low_count):
        """根據約束條件生成號碼"""
        # 這是一個簡化的實現，實際可以使用更複雜的約束求解
        attempts = 0
        max_attempts = 1000
        
        while attempts < max_attempts:
            numbers = random.sample(range(1, 50), self.numbers_to_pick)
            
            current_sum = sum(numbers)
            current_range = max(numbers) - min(numbers)
            current_odd_count = len([n for n in numbers if n % 2 == 1])
            current_low_count = len([n for n in numbers if n <= 24])
            
            # 檢查是否接近目標
            sum_diff = abs(current_sum - target_sum)
            range_diff = abs(current_range - target_range)
            odd_diff = abs(current_odd_count - target_odd_count)
            low_diff = abs(current_low_count - target_low_count)
            
            # 如果足夠接近，接受這組號碼
            if sum_diff <= 20 and range_diff <= 10 and odd_diff <= 1 and low_diff <= 1:
                return numbers
            
            attempts += 1
        
        # 如果無法找到符合約束的號碼，返回隨機號碼
        return random.sample(range(1, 50), self.numbers_to_pick)
    
    def _calculate_confidence(self, data, predicted_numbers, predicted_special):
        """計算預測信心度"""
        if not data:
            return 0.5
        
        # 基於多個因素計算信心度
        confidence_factors = []
        
        # 1. 號碼頻率一致性
        number_freq = Counter()
        for record in data:
            for num in record['numbers']:
                number_freq[num] += 1
        
        avg_freq = sum(number_freq.values()) / len(number_freq) if number_freq else 0
        predicted_freq_score = sum(number_freq.get(num, 0) for num in predicted_numbers) / len(predicted_numbers)
        freq_confidence = min(predicted_freq_score / (avg_freq + 1), 1.0)
        confidence_factors.append(freq_confidence)
        
        # 2. 模式一致性
        patterns = self._analyze_patterns(data)
        predicted_odd_count = len([n for n in predicted_numbers if n % 2 == 1])
        predicted_low_count = len([n for n in predicted_numbers if n <= 24])
        
        odd_consistency = 1 - abs(predicted_odd_count - patterns['avg_odd_count']) / 6
        low_consistency = 1 - abs(predicted_low_count - patterns['avg_low_count']) / 6
        confidence_factors.extend([odd_consistency, low_consistency])
        
        # 3. 資料量因子
        data_factor = min(len(data) / 20, 1.0)  # 20期以上資料較可靠
        confidence_factors.append(data_factor)
        
        # 計算綜合信心度
        final_confidence = sum(confidence_factors) / len(confidence_factors)
        
        # 加入隨機性，避免過度自信
        final_confidence *= random.uniform(0.8, 1.0)
        
        return round(min(max(final_confidence, 0.1), 0.9), 3)


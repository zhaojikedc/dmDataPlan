#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术分析模块 - 计算各种技术指标
不依赖talib，使用pandas和numpy实现
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, Optional, List
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """技术分析器 - 计算各种技术指标"""
    
    def __init__(self):
        """初始化技术分析器"""
        self.logger = logger
    
    def calculate_ma(self, data: pd.Series, period: int) -> pd.Series:
        """计算移动平均线"""
        try:
            return data.rolling(window=period).mean()
        except Exception as e:
            self.logger.error(f"计算MA({period})失败: {e}")
            return pd.Series(index=data.index)
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均线"""
        try:
            return data.ewm(span=period).mean()
        except Exception as e:
            self.logger.error(f"计算EMA({period})失败: {e}")
            return pd.Series(index=data.index)
    
    def calculate_macd(self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """计算MACD指标"""
        try:
            ema_fast = self.calculate_ema(data, fast)
            ema_slow = self.calculate_ema(data, slow)
            macd_line = ema_fast - ema_slow
            signal_line = self.calculate_ema(macd_line, signal)
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
        except Exception as e:
            self.logger.error(f"计算MACD失败: {e}")
            return {'macd': pd.Series(), 'signal': pd.Series(), 'histogram': pd.Series()}
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        try:
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            self.logger.error(f"计算RSI失败: {e}")
            return pd.Series(index=data.index)
    
    def calculate_bollinger_bands(self, data: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """计算布林带"""
        try:
            ma = self.calculate_ma(data, period)
            std = data.rolling(window=period).std()
            upper_band = ma + (std * std_dev)
            lower_band = ma - (std * std_dev)
            
            return {
                'upper': upper_band,
                'middle': ma,
                'lower': lower_band,
                'width': (upper_band - lower_band) / ma * 100
            }
        except Exception as e:
            self.logger.error(f"计算布林带失败: {e}")
            return {'upper': pd.Series(), 'middle': pd.Series(), 'lower': pd.Series(), 'width': pd.Series()}
    
    def calculate_kdj(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                     k_period: int = 9, d_period: int = 3, j_period: int = 3) -> Dict[str, pd.Series]:
        """计算KDJ指标"""
        try:
            # 计算RSV
            low_min = low.rolling(window=k_period).min()
            high_max = high.rolling(window=k_period).max()
            rsv = 100 * (close - low_min) / (high_max - low_min)
            
            # 计算K值
            k = pd.Series(index=rsv.index, dtype=float)
            k.iloc[0] = 50
            for i in range(1, len(rsv)):
                k.iloc[i] = (2/3) * k.iloc[i-1] + (1/3) * rsv.iloc[i]
            
            # 计算D值
            d = pd.Series(index=k.index, dtype=float)
            d.iloc[0] = 50
            for i in range(1, len(k)):
                d.iloc[i] = (2/3) * d.iloc[i-1] + (1/3) * k.iloc[i]
            
            # 计算J值
            j = 3 * k - 2 * d
            
            return {'k': k, 'd': d, 'j': j}
        except Exception as e:
            self.logger.error(f"计算KDJ失败: {e}")
            return {'k': pd.Series(), 'd': pd.Series(), 'j': pd.Series()}
    
    def calculate_momentum(self, data: pd.Series, period: int = 10) -> pd.Series:
        """计算动量指标"""
        try:
            return data / data.shift(period) * 100
        except Exception as e:
            self.logger.error(f"计算动量指标失败: {e}")
            return pd.Series(index=data.index)
    
    def calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """计算威廉指标%R"""
        try:
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
            return williams_r
        except Exception as e:
            self.logger.error(f"计算威廉指标失败: {e}")
            return pd.Series(index=close.index)
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                           k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """计算随机指标"""
        try:
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            k = 100 * (close - lowest_low) / (highest_high - lowest_low)
            d = k.rolling(window=d_period).mean()
            
            return {'k': k, 'd': d}
        except Exception as e:
            self.logger.error(f"计算随机指标失败: {e}")
            return {'k': pd.Series(), 'd': pd.Series()}
    
    def calculate_volatility(self, data: pd.Series, period: int = 20) -> pd.Series:
        """计算波动率"""
        try:
            returns = data.pct_change()
            volatility = returns.rolling(window=period).std() * np.sqrt(252) * 100
            return volatility
        except Exception as e:
            self.logger.error(f"计算波动率失败: {e}")
            return pd.Series(index=data.index)
    
    def calculate_support_resistance(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                                   period: int = 20) -> Dict[str, float]:
        """计算支撑位和阻力位"""
        try:
            recent_high = high.tail(period).max()
            recent_low = low.tail(period).min()
            current_price = close.iloc[-1]
            
            # 计算支撑位和阻力位
            resistance = recent_high + (recent_high - recent_low) * 0.1
            support = recent_low - (recent_high - recent_low) * 0.1
            
            return {
                'support': support,
                'resistance': resistance,
                'current_price': current_price,
                'distance_to_support': ((current_price - support) / current_price) * 100,
                'distance_to_resistance': ((resistance - current_price) / current_price) * 100
            }
        except Exception as e:
            self.logger.error(f"计算支撑阻力位失败: {e}")
            return {}
    
    def generate_trading_signals(self, data: pd.DataFrame) -> Dict[str, int]:
        """生成交易信号"""
        try:
            signals = {}
            
            # RSI信号
            if 'rsi' in data.columns:
                rsi = data['rsi'].iloc[-1]
                if rsi < 30:
                    signals['rsi_signal'] = 1  # 超卖，买入信号
                elif rsi > 70:
                    signals['rsi_signal'] = -1  # 超买，卖出信号
                else:
                    signals['rsi_signal'] = 0  # 中性
            
            # MACD信号
            if 'macd' in data.columns and 'macd_signal' in data.columns:
                macd = data['macd'].iloc[-1]
                macd_signal = data['macd_signal'].iloc[-1]
                if macd > macd_signal:
                    signals['macd_signal'] = 1  # 金叉，买入信号
                else:
                    signals['macd_signal'] = -1  # 死叉，卖出信号
            
            # 布林带信号
            if 'close' in data.columns and 'bb_upper' in data.columns and 'bb_lower' in data.columns:
                close = data['close'].iloc[-1]
                bb_upper = data['bb_upper'].iloc[-1]
                bb_lower = data['bb_lower'].iloc[-1]
                
                if close < bb_lower:
                    signals['bb_signal'] = 1  # 价格触及下轨，买入信号
                elif close > bb_upper:
                    signals['bb_signal'] = -1  # 价格触及上轨，卖出信号
                else:
                    signals['bb_signal'] = 0  # 价格在轨道内，中性
            
            # 综合信号
            if signals:
                # 计算综合信号强度
                signal_values = list(signals.values())
                avg_signal = sum(signal_values) / len(signal_values)
                
                if avg_signal > 0.3:
                    signals['overall_signal'] = 1  # 买入
                elif avg_signal < -0.3:
                    signals['overall_signal'] = -1  # 卖出
                else:
                    signals['overall_signal'] = 0  # 持有
                
                signals['signal_strength'] = abs(avg_signal)
            else:
                signals['overall_signal'] = 0
                signals['signal_strength'] = 0
            
            return signals
            
        except Exception as e:
            self.logger.error(f"生成交易信号失败: {e}")
            return {'overall_signal': 0, 'signal_strength': 0}
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        try:
            result = data.copy()
            
            # 确保必要的列存在
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in result.columns:
                    self.logger.warning(f"缺少必要的列: {col}")
                    return result
            
            # 计算移动平均线
            result['ma5'] = self.calculate_ma(result['close'], 5)
            result['ma10'] = self.calculate_ma(result['close'], 10)
            result['ma20'] = self.calculate_ma(result['close'], 20)
            result['ma60'] = self.calculate_ma(result['close'], 60)
            
            # 计算指数移动平均线
            result['ema12'] = self.calculate_ema(result['close'], 12)
            result['ema26'] = self.calculate_ema(result['close'], 26)
            
            # 计算MACD
            macd_data = self.calculate_macd(result['close'])
            result['macd'] = macd_data['macd']
            result['macd_signal'] = macd_data['signal']
            result['macd_histogram'] = macd_data['histogram']
            
            # 计算RSI
            result['rsi'] = self.calculate_rsi(result['close'])
            
            # 计算布林带
            bb_data = self.calculate_bollinger_bands(result['close'])
            result['bb_upper'] = bb_data['upper']
            result['bb_middle'] = bb_data['middle']
            result['bb_lower'] = bb_data['lower']
            result['bb_width'] = bb_data['width']
            
            # 计算KDJ
            kdj_data = self.calculate_kdj(result['high'], result['low'], result['close'])
            result['kdj_k'] = kdj_data['k']
            result['kdj_d'] = kdj_data['d']
            result['kdj_j'] = kdj_data['j']
            
            # 计算动量指标
            result['momentum'] = self.calculate_momentum(result['close'])
            
            # 计算威廉指标
            result['williams_r'] = self.calculate_williams_r(result['high'], result['low'], result['close'])
            
            # 计算随机指标
            stoch_data = self.calculate_stochastic(result['high'], result['low'], result['close'])
            result['stoch_k'] = stoch_data['k']
            result['stoch_d'] = stoch_data['d']
            
            # 计算波动率
            result['volatility'] = self.calculate_volatility(result['close'])
            
            # 计算价格变化
            result['price_change'] = result['close'].pct_change() * 100
            result['price_change_5d'] = result['close'].pct_change(5) * 100
            result['price_change_20d'] = result['close'].pct_change(20) * 100
            
            # 计算成交量指标
            result['volume_ma5'] = self.calculate_ma(result['volume'], 5)
            result['volume_ma20'] = self.calculate_ma(result['volume'], 20)
            result['volume_ratio'] = result['volume'] / result['volume_ma20']
            
            self.logger.info("所有技术指标计算完成")
            return result
            
        except Exception as e:
            self.logger.error(f"计算技术指标失败: {e}")
            return data
    
    def get_latest_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """获取最新的技术指标值"""
        try:
            latest = data.iloc[-1]
            indicators = {}
            
            # 价格相关
            if 'close' in latest:
                indicators['close'] = latest['close']
            if 'price_change' in latest:
                indicators['price_change'] = latest['price_change']
            
            # 移动平均线
            for ma in ['ma5', 'ma10', 'ma20', 'ma60']:
                if ma in latest and pd.notna(latest[ma]):
                    indicators[ma] = latest[ma]
            
            # 技术指标
            for indicator in ['rsi', 'macd', 'bb_width', 'volatility']:
                if indicator in latest and pd.notna(latest[indicator]):
                    indicators[indicator] = latest[indicator]
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"获取最新指标失败: {e}")
            return {}
    
    def analyze_trend(self, data: pd.DataFrame) -> str:
        """分析趋势"""
        try:
            if len(data) < 20:
                return "insufficient_data"
            
            # 获取最新的价格和均线数据
            latest_close = data['close'].iloc[-1]
            ma20 = data['ma20'].iloc[-1]
            ma60 = data['ma60'].iloc[-1]
            
            # 计算短期趋势
            ma5 = data['ma5'].iloc[-1]
            ma10 = data['ma10'].iloc[-1]
            
            # 判断趋势
            if pd.notna(ma5) and pd.notna(ma10) and pd.notna(ma20) and pd.notna(ma60):
                if ma5 > ma10 > ma20 > ma60 and latest_close > ma5:
                    return "strong_bullish"
                elif ma5 > ma10 > ma20 and latest_close > ma5:
                    return "bullish"
                elif ma5 < ma10 < ma20 < ma60 and latest_close < ma5:
                    return "strong_bearish"
                elif ma5 < ma10 < ma20 and latest_close < ma5:
                    return "bearish"
                else:
                    return "neutral"
            else:
                return "insufficient_data"
                
        except Exception as e:
            self.logger.error(f"分析趋势失败: {e}")
            return "error"

if __name__ == "__main__":
    # 测试代码
    analyzer = TechnicalAnalyzer()
    print("技术分析器初始化成功")

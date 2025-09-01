#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析器主类
整合数据获取、技术分析和机器学习预测功能
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from stock_data_fetcher import StockDataFetcher
from technical_analyzer import TechnicalAnalyzer
from ml_predictor import StockPredictor

logger = logging.getLogger(__name__)

class StockAnalyzer:
    """股票分析器主类"""
    
    def __init__(self):
        self.data_fetcher = StockDataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        self.predictor = StockPredictor()
        
    def analyze_stock(self, stock_code: str, days: int = 365, prediction_days: int = 5) -> Dict:
        """分析单只股票"""
        try:
            logger.info(f"开始分析股票: {stock_code}")
            
            # 获取历史数据
            history_data = self.data_fetcher.get_stock_history(stock_code, days)
            if history_data.empty:
                return {'error': '无法获取股票数据'}
            
            # 计算技术指标
            indicators_data = self.technical_analyzer.calculate_all_indicators(history_data)
            
            # 生成交易信号
            signals_data = self.technical_analyzer.generate_trading_signals(indicators_data)
            
            # 计算支撑阻力位
            support_resistance = self.technical_analyzer.calculate_support_resistance(
                indicators_data['high'], indicators_data['low'], indicators_data['close']
            )
            
            # 分析趋势
            trend = self.technical_analyzer.analyze_trend(indicators_data)
            
            # 获取最新指标
            latest_indicators = self.technical_analyzer.get_latest_indicators(indicators_data)
            
            # 生成分析报告
            analysis_report = {
                'stock_code': stock_code,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_period': f"{indicators_data.index[0].strftime('%Y-%m-%d')} 至 {indicators_data.index[-1].strftime('%Y-%m-%d')}",
                'current_price': float(indicators_data['close'].iloc[-1]),
                'price_change': float(indicators_data['price_change'].iloc[-1]) if 'price_change' in indicators_data.columns else 0,
                'price_change_pct': float(indicators_data['price_change'].iloc[-1]) if 'price_change' in indicators_data.columns else 0,
                'volume': float(indicators_data['volume'].iloc[-1]),
                'technical_indicators': {
                    'rsi': float(indicators_data['rsi'].iloc[-1]) if 'rsi' in indicators_data.columns else 0,
                    'macd': float(indicators_data['macd'].iloc[-1]) if 'macd' in indicators_data.columns else 0,
                    'bb_position': float((indicators_data['close'].iloc[-1] - indicators_data['bb_lower'].iloc[-1]) / 
                                       (indicators_data['bb_upper'].iloc[-1] - indicators_data['bb_lower'].iloc[-1])) if 'bb_upper' in indicators_data.columns else 0,
                    'ma_trend': 'bullish' if indicators_data['close'].iloc[-1] > indicators_data['ma20'].iloc[-1] else 'bearish',
                    'kdj_k': float(indicators_data['kdj_k'].iloc[-1]) if 'kdj_k' in indicators_data.columns else 0,
                    'kdj_d': float(indicators_data['kdj_d'].iloc[-1]) if 'kdj_d' in indicators_data.columns else 0,
                    'kdj_j': float(indicators_data['kdj_j'].iloc[-1]) if 'kdj_j' in indicators_data.columns else 0
                },
                'trading_signals': {
                    'current_signal': int(signals_data.get('overall_signal', 0)),
                    'signal_strength': float(signals_data.get('signal_strength', 0))
                },
                'support_resistance': support_resistance,
                'volatility': {
                    'current_volatility': float(indicators_data['volatility'].iloc[-1]) if 'volatility' in indicators_data.columns else 0,
                    'trend': trend
                },
                'recommendation': self._generate_recommendation(indicators_data, signals_data, support_resistance),
                'risk_assessment': self._assess_risk(indicators_data, signals_data)
            }
            
            logger.info(f"股票 {stock_code} 分析完成")
            return analysis_report
            
        except Exception as e:
            logger.error(f"分析股票 {stock_code} 失败: {e}")
            return {'error': f'分析失败: {str(e)}'}
    
    def batch_analyze(self, stock_codes: List[str], days: int = 365, prediction_days: int = 5) -> List[Dict]:
        """批量分析股票"""
        results = []
        for stock_code in stock_codes:
            try:
                result = self.analyze_stock(stock_code, days, prediction_days)
                results.append(result)
                logger.info(f"批量分析完成: {stock_code}")
            except Exception as e:
                logger.error(f"批量分析失败: {stock_code}, 错误: {e}")
                results.append({'stock_code': stock_code, 'error': str(e)})
        
        return results
    
    def analyze_market_sentiment(self, stock_list: pd.DataFrame, top_n: int = 100) -> Dict:
        """分析市场情绪"""
        try:
            if stock_list.empty:
                return {'error': '股票列表为空'}
            
            # 选择前N只股票进行分析
            top_stocks = stock_list.head(top_n)
            
            # 计算市场情绪指标
            up_stocks = len(top_stocks[top_stocks['change_pct'] > 0])
            down_stocks = len(top_stocks[top_stocks['change_pct'] < 0])
            flat_stocks = len(top_stocks[top_stocks['change_pct'] == 0])
            
            avg_change = top_stocks['change_pct'].mean()
            avg_volume = top_stocks['volume'].mean()
            
            # 判断市场情绪
            if up_stocks > down_stocks * 1.5:
                sentiment = 'bullish'
            elif down_stocks > up_stocks * 1.5:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
            
            return {
                'total_stocks': len(top_stocks),
                'up_stocks': up_stocks,
                'down_stocks': down_stocks,
                'flat_stocks': flat_stocks,
                'up_ratio': up_stocks / len(top_stocks),
                'down_ratio': down_stocks / len(top_stocks),
                'avg_change': avg_change,
                'avg_volume': avg_volume,
                'sentiment': sentiment
            }
            
        except Exception as e:
            logger.error(f"市场情绪分析失败: {e}")
            return {'error': f'市场情绪分析失败: {str(e)}'}
    
    def _generate_recommendation(self, data: pd.DataFrame, signals: Dict, support_resistance: Dict) -> str:
        """生成投资建议"""
        try:
            if 'error' in signals:
                return "数据不足，无法生成建议"
            
            signal = signals.get('overall_signal', 0)
            strength = signals.get('signal_strength', 0)
            
            if signal == 1 and strength > 0.5:
                return "强烈买入：技术指标显示强烈买入信号"
            elif signal == 1:
                return "买入：技术指标显示买入信号"
            elif signal == -1 and strength > 0.5:
                return "强烈卖出：技术指标显示强烈卖出信号"
            elif signal == -1:
                return "卖出：技术指标显示卖出信号"
            else:
                return "持有：技术指标显示中性信号，建议观望"
                
        except Exception as e:
            logger.error(f"生成投资建议失败: {e}")
            return "无法生成投资建议"
    
    def _assess_risk(self, data: pd.DataFrame, signals: Dict) -> Dict:
        """评估风险"""
        try:
            risk_assessment = {
                'overall_risk': 'medium',
                'volatility_risk': 'medium',
                'rsi_risk': 'medium'
            }
            
            # 评估波动率风险
            if 'volatility' in data.columns:
                current_vol = data['volatility'].iloc[-1]
                if pd.notna(current_vol):
                    if current_vol > 30:
                        risk_assessment['volatility_risk'] = 'high'
                    elif current_vol < 15:
                        risk_assessment['volatility_risk'] = 'low'
            
            # 评估RSI风险
            if 'rsi' in data.columns:
                current_rsi = data['rsi'].iloc[-1]
                if pd.notna(current_rsi):
                    if current_rsi > 80 or current_rsi < 20:
                        risk_assessment['rsi_risk'] = 'high'
                    elif current_rsi > 70 or current_rsi < 30:
                        risk_assessment['rsi_risk'] = 'medium'
                    else:
                        risk_assessment['rsi_risk'] = 'low'
            
            # 综合风险评估
            high_risk_count = sum(1 for risk in risk_assessment.values() if risk == 'high')
            if high_risk_count >= 2:
                risk_assessment['overall_risk'] = 'high'
            elif high_risk_count == 0:
                risk_assessment['overall_risk'] = 'low'
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"风险评估失败: {e}")
            return {'overall_risk': 'unknown', 'volatility_risk': 'unknown', 'rsi_risk': 'unknown'}
    
    def save_analysis_report(self, report: Dict, filename: str) -> bool:
        """保存分析报告"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"分析报告已保存: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存分析报告失败: {e}")
            return False
    
    def save_batch_report(self, reports: List[Dict], filename: str) -> bool:
        """保存批量分析报告"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(reports, f, ensure_ascii=False, indent=2)
            logger.info(f"批量分析报告已保存: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存批量分析报告失败: {e}")
            return False
    
    def generate_summary_report(self, reports: List[Dict]) -> str:
        """生成汇总报告"""
        try:
            successful_reports = [r for r in reports if 'error' not in r]
            failed_reports = [r for r in reports if 'error' in r]
            
            summary = f"""
汇总报告
========
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总股票数: {len(reports)}
成功分析: {len(successful_reports)}
分析失败: {len(failed_reports)}

成功分析股票:
"""
            for report in successful_reports:
                summary += f"- {report['stock_code']}: {report['recommendation']}\n"
            
            if failed_reports:
                summary += "\n分析失败股票:\n"
                for report in failed_reports:
                    summary += f"- {report['stock_code']}: {report['error']}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"生成汇总报告失败: {e}")
            return f"生成汇总报告失败: {str(e)}"

if __name__ == "__main__":
    analyzer = StockAnalyzer()
    print("股票分析器初始化成功")

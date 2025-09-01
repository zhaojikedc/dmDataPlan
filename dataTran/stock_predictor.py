#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国股市预测分析系统
支持调取互联网股市历史数据，进行技术分析和机器学习预测
"""

import os
import sys
import time
import json
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Tuple, Optional
import logging

# 机器学习相关
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression

# 技术分析相关
import talib
from talib import abstract

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_predictor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        try:
            # 使用东方财富网API获取股票列表
            url = "http://80.push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 5000,
                'po': 1,
                'np': 1,
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': 'm:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23',
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data['rc'] == 0 and 'data' in data:
                stocks = []
                for item in data['data']['diff']:
                    stocks.append({
                        'code': item['f12'],
                        'name': item['f14'],
                        'price': item['f2'] / 100,
                        'change': item['f3'] / 100,
                        'change_pct': item['f4'] / 100,
                        'volume': item['f5'],
                        'amount': item['f6'],
                        'market_cap': item['f15'] / 100000000,  # 亿元
                        'pe': item['f9'] / 100,
                        'pb': item['f10'] / 100
                    })
                
                df = pd.DataFrame(stocks)
                logger.info(f"成功获取 {len(df)} 只股票信息")
                return df
            else:
                logger.error("获取股票列表失败")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取股票列表异常: {e}")
            return pd.DataFrame()
    
    def get_stock_history(self, stock_code: str, days: int = 365) -> pd.DataFrame:
        """获取股票历史数据"""
        try:
            # 使用东方财富网API获取历史数据
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': f'1.{stock_code}' if stock_code.startswith('6') else f'0.{stock_code}',
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': 101,  # 日K线
                'fqt': 1,    # 前复权
                'beg': 0,
                'end': 20500101,
                'smplmt': days,
                'lmt': days
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data['rc'] == 0 and 'data' in data:
                klines = data['data']['klines']
                history_data = []
                
                for kline in klines:
                    parts = kline.split(',')
                    history_data.append({
                        'date': parts[0],
                        'open': float(parts[1]),
                        'close': float(parts[2]),
                        'high': float(parts[3]),
                        'low': float(parts[4]),
                        'volume': float(parts[5]),
                        'amount': float(parts[6]),
                        'amplitude': float(parts[7]),
                        'change_pct': float(parts[8]),
                        'change': float(parts[9]),
                        'turnover': float(parts[10])
                    })
                
                df = pd.DataFrame(history_data)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                
                logger.info(f"成功获取 {stock_code} 的 {len(df)} 天历史数据")
                return df
            else:
                logger.error(f"获取 {stock_code} 历史数据失败")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取 {stock_code} 历史数据异常: {e}")
            return pd.DataFrame()

def main():
    """主函数"""
    try:
        print("=" * 60)
        print("中国股市预测分析系统")
        print("=" * 60)
        
        # 创建数据获取器
        fetcher = StockDataFetcher()
        
        # 获取股票列表
        print("\n正在获取股票列表...")
        stock_list = fetcher.get_stock_list()
        
        if stock_list.empty:
            print("获取股票列表失败")
            return
        
        print(f"成功获取 {len(stock_list)} 只股票")
        
        # 显示部分股票信息
        print("\n股票列表预览:")
        print(stock_list.head(10)[['code', 'name', 'price', 'change_pct', 'market_cap']].to_string(index=False))
        
        # 测试获取单只股票数据
        test_code = input("\n请输入要测试的股票代码 (如: 000001): ").strip()
        if test_code:
            print(f"\n正在获取 {test_code} 的历史数据...")
            history = fetcher.get_stock_history(test_code, 30)
            if not history.empty:
                print(f"成功获取 {test_code} 的30天数据:")
                print(history.tail())
            else:
                print(f"获取 {test_code} 数据失败")
        
        print("\n测试完成！")
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"程序异常: {e}")

if __name__ == "__main__":
    main()

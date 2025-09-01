#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取器模块
负责从互联网获取股票数据
"""

import pandas as pd
import numpy as np
import requests
import time
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 设置请求超时和重试
        self.timeout = 10
        self.max_retries = 3
        
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
            
            response = self._make_request(url, params)
            if not response:
                return pd.DataFrame()
            
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
            
            response = self._make_request(url, params)
            if not response:
                return pd.DataFrame()
            
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
    
    def get_realtime_quote(self, stock_codes: List[str]) -> pd.DataFrame:
        """获取实时行情数据"""
        try:
            if not stock_codes:
                return pd.DataFrame()
            
            # 批量获取实时数据
            url = "http://push2.eastmoney.com/api/qt/ulist.np/get"
            
            # 构建股票代码字符串
            secids = []
            for code in stock_codes:
                market = '1' if code.startswith('6') else '0'
                secids.append(f"{market}.{code}")
            
            secids_str = ','.join(secids)
            
            params = {
                'secids': secids_str,
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': 2,
                'invt': 2,
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152'
            }
            
            response = self._make_request(url, params)
            if not response:
                return pd.DataFrame()
            
            data = response.json()
            
            if data['rc'] == 0 and 'data' in data:
                quotes = []
                for item in data['data']['diff']:
                    quotes.append({
                        'code': item['f12'],
                        'name': item['f14'],
                        'price': item['f2'] / 100,
                        'change': item['f3'] / 100,
                        'change_pct': item['f4'] / 100,
                        'volume': item['f5'],
                        'amount': item['f6'],
                        'open': item['f17'] / 100,
                        'high': item['f15'] / 100,
                        'low': item['f16'] / 100,
                        'prev_close': item['f18'] / 100,
                        'turnover': item['f8'] / 100,
                        'market_cap': item['f20'] / 100000000,
                        'pe': item['f9'] / 100,
                        'pb': item['f23'] / 100
                    })
                
                df = pd.DataFrame(quotes)
                logger.info(f"成功获取 {len(df)} 只股票的实时行情")
                return df
            else:
                logger.error("获取实时行情失败")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取实时行情异常: {e}")
            return pd.DataFrame()
    
    def get_stock_news(self, stock_code: str, days: int = 7) -> List[Dict]:
        """获取股票相关新闻"""
        try:
            # 使用东方财富网新闻API
            url = "http://np-anotice-stock.eastmoney.com/api/security/announcement/getAnnouncementList"
            
            params = {
                'pageSize': 20,
                'pageNum': 1,
                'column': 'szjs',
                'tabName': 'fulltext',
                'plate': 'sz',
                'stock': stock_code,
                'searchkey': '',
                'secid': '',
                'category': '',
                'trade': '',
                'seDate': f"{(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')}~{datetime.now().strftime('%Y-%m-%d')}"
            }
            
            response = self._make_request(url, params)
            if not response:
                return []
            
            data = response.json()
            
            if data['success'] and 'data' in data:
                news_list = []
                for item in data['data']['list']:
                    news_list.append({
                        'title': item['title'],
                        'date': item['notice_date'],
                        'url': f"http://static.eastmoney.com/notices/{item['adjunctUrl']}",
                        'type': item['column']
                    })
                
                logger.info(f"成功获取 {stock_code} 的 {len(news_list)} 条新闻")
                return news_list
            else:
                logger.error(f"获取 {stock_code} 新闻失败")
                return []
                
        except Exception as e:
            logger.error(f"获取 {stock_code} 新闻异常: {e}")
            return []
    
    def get_market_index(self) -> pd.DataFrame:
        """获取主要指数数据"""
        try:
            # 主要指数代码
            indices = {
                '000001': '上证指数',
                '399001': '深证成指',
                '399006': '创业板指',
                '000300': '沪深300',
                '000905': '中证500',
                '000016': '上证50'
            }
            
            indices_data = []
            
            for code, name in indices.items():
                try:
                    # 获取指数数据
                    url = "http://push2.eastmoney.com/api/qt/stock/get"
                    params = {
                        'secid': f'1.{code}',
                        'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                        'fields': 'f43,f57,f58,f169,f170,f46,f44,f51,f168,f47'
                    }
                    
                    response = self._make_request(url, params)
                    if response:
                        data = response.json()
                        if data['rc'] == 0 and 'data' in data:
                            item = data['data']
                            indices_data.append({
                                'code': code,
                                'name': name,
                                'price': item['f43'] / 100,
                                'change': item['f170'] / 100,
                                'change_pct': item['f169'] / 100,
                                'volume': item['f47'] / 100,
                                'amount': item['f48'] / 100000000
                            })
                    
                    time.sleep(0.1)  # 避免请求过快
                    
                except Exception as e:
                    logger.error(f"获取指数 {code} 数据失败: {e}")
                    continue
            
            df = pd.DataFrame(indices_data)
            logger.info(f"成功获取 {len(df)} 个主要指数数据")
            return df
            
        except Exception as e:
            logger.error(f"获取主要指数异常: {e}")
            return pd.DataFrame()
    
    def get_industry_data(self) -> pd.DataFrame:
        """获取行业板块数据"""
        try:
            # 获取行业板块数据
            url = "http://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 100,
                'po': 1,
                'np': 1,
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': 'b:BK0707',
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18'
            }
            
            response = self._make_request(url, params)
            if not response:
                return pd.DataFrame()
            
            data = response.json()
            
            if data['rc'] == 0 and 'data' in data:
                industries = []
                for item in data['data']['diff']:
                    industries.append({
                        'code': item['f12'],
                        'name': item['f14'],
                        'price': item['f2'] / 100,
                        'change': item['f3'] / 100,
                        'change_pct': item['f4'] / 100,
                        'volume': item['f5'],
                        'amount': item['f6'],
                        'stock_count': item['f15']
                    })
                
                df = pd.DataFrame(industries)
                logger.info(f"成功获取 {len(df)} 个行业板块数据")
                return df
            else:
                logger.error("获取行业板块数据失败")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取行业板块数据异常: {e}")
            return pd.DataFrame()
    
    def _make_request(self, url: str, params: Dict, retries: int = 0) -> Optional[requests.Response]:
        """发送HTTP请求，支持重试"""
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            if retries < self.max_retries:
                logger.warning(f"请求失败，重试 {retries + 1}/{self.max_retries}: {e}")
                time.sleep(2 ** retries)  # 指数退避
                return self._make_request(url, params, retries + 1)
            else:
                logger.error(f"请求失败，已达到最大重试次数: {e}")
                return None
    
    def save_data_to_csv(self, df: pd.DataFrame, filename: str):
        """保存数据到CSV文件"""
        try:
            df.to_csv(filename, encoding='utf-8-sig', index=True)
            logger.info(f"数据已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存CSV文件失败: {e}")
    
    def save_data_to_json(self, data: Dict, filename: str):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"数据已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
    
    def get_stock_financial_data(self, stock_code: str) -> Dict:
        """获取股票财务数据"""
        try:
            # 获取财务指标
            url = "http://f10.eastmoney.com/api/qt/stock/get"
            params = {
                'secid': f'1.{stock_code}' if stock_code.startswith('6') else f'0.{stock_code}',
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'fields': 'f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167'
            }
            
            response = self._make_request(url, params)
            if not response:
                return {}
            
            data = response.json()
            
            if data['rc'] == 0 and 'data' in data:
                item = data['data']
                financial_data = {
                    'code': stock_code,
                    'pe_ttm': item.get('f162', 0) / 100,  # 市盈率TTM
                    'pb': item.get('f167', 0) / 100,       # 市净率
                    'ps_ttm': item.get('f164', 0) / 100,   # 市销率TTM
                    'pcf_ttm': item.get('f165', 0) / 100,  # 市现率TTM
                    'roe': item.get('f170', 0) / 100,      # 净资产收益率
                    'roa': item.get('f171', 0) / 100,      # 总资产收益率
                    'debt_ratio': item.get('f172', 0) / 100, # 资产负债率
                    'current_ratio': item.get('f173', 0) / 100, # 流动比率
                    'quick_ratio': item.get('f174', 0) / 100,   # 速动比率
                    'gross_margin': item.get('f175', 0) / 100,  # 毛利率
                    'net_margin': item.get('f176', 0) / 100,    # 净利率
                }
                
                logger.info(f"成功获取 {stock_code} 的财务数据")
                return financial_data
            else:
                logger.error(f"获取 {stock_code} 财务数据失败")
                return {}
                
        except Exception as e:
            logger.error(f"获取 {stock_code} 财务数据异常: {e}")
            return {}









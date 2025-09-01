#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国股市预测分析系统 - 快速启动脚本
提供简单的使用示例和演示
"""

import sys
import os
import time
import locale
from datetime import datetime

# 设置编码处理
if sys.platform.startswith('win'):
    # Windows系统编码处理
    try:
        # 尝试设置控制台编码为UTF-8
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass
    
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
try:
    from stock_data_fetcher import StockDataFetcher
    from stock_analyzer import StockAnalyzer
    print("✓ 所有模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败: {e}")
    print("请确保所有必需文件都在dataTran目录中")
    sys.exit(1)

def main():
    """主函数 - 快速启动演示"""
    try:
        print("=" * 60)
        print("中国股市预测分析系统 - 快速启动")
        print("=" * 60)
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 导入必要的模块
        print("正在导入模块...")
        print("✓ 模块导入成功")
        print()
        
        # 创建数据获取器
        print("正在初始化数据获取器...")
        fetcher = StockDataFetcher()
        print("✓ 数据获取器初始化成功")
        print()
        
        # 获取股票列表
        print("正在获取股票列表...")
        stock_list = fetcher.get_stock_list()
        if stock_list.empty:
            print("✗ 获取股票列表失败")
            return
        print(f"✓ 成功获取 {len(stock_list)} 只股票")
        print()
        
        # 显示股票列表预览
        print("股票列表预览:")
        preview = stock_list.head(10)[['code', 'name', 'price', 'change_pct', 'market_cap']]
        print(preview.to_string(index=False))
        print()
        
        # 用户选择分析模式
        print("请选择分析模式:")
        print("1. 分析单只股票")
        print("2. 分析热门股票")
        print("3. 市场情绪分析")
        print("4. 退出")
        print()
        
        while True:
            choice = input("请输入选择 (1-4): ").strip()
            
            if choice == '1':
                # 单只股票分析
                stock_code = input("请输入股票代码 (如: 000001): ").strip()
                if stock_code:
                    analyze_single_stock(stock_code)
                break
                
            elif choice == '2':
                # 热门股票分析
                analyze_hot_stocks(stock_list)
                break
                
            elif choice == '3':
                # 市场情绪分析
                analyze_market_sentiment(stock_list)
                break
                
            elif choice == '4':
                print("感谢使用！")
                break
                
            else:
                print("无效选择，请重新输入")
                print()
        
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        print("请确保已安装所有依赖包:")
        print("pip install -r requirements.txt")
        
    except Exception as e:
        print(f"✗ 系统启动失败: {e}")
        print("请检查网络连接和系统配置")

def analyze_single_stock(stock_code):
    """分析单只股票"""
    print(f"\n正在分析股票: {stock_code}")
    print("-" * 40)
    
    try:
        # 创建分析器
        analyzer = StockAnalyzer()
        
        # 分析股票
        print("正在获取历史数据...")
        result = analyzer.analyze_stock(stock_code, days=365, prediction_days=5)
        
        if 'error' in result:
            print(f"✗ 分析失败: {result['error']}")
            return
        
        # 显示分析结果
        print("✓ 分析完成！")
        print()
        print("分析结果:")
        print(f"  股票代码: {result['stock_code']}")
        print(f"  分析时间: {result['analysis_date']}")
        print(f"  数据周期: {result['data_period']}")
        print(f"  当前价格: {result['current_price']:.2f}")
        print(f"  涨跌幅: {result['price_change_pct']:.2f}%")
        print(f"  成交量: {result['volume']:,.0f}")
        print()
        
        print("技术指标:")
        tech = result['technical_indicators']
        print(f"  RSI: {tech['rsi']:.2f}")
        print(f"  MACD: {tech['macd']:.4f}")
        print(f"  布林带位置: {tech['bb_position']:.2f}")
        print(f"  均线趋势: {'看涨' if tech['ma_trend'] == 'bullish' else '看跌'}")
        print()
        
        print("交易信号:")
        signals = result['trading_signals']
        signal_text = {1: '买入', 0: '持有', -1: '卖出'}
        print(f"  当前信号: {signal_text[signals['current_signal']]}")
        print(f"  信号强度: {signals['signal_strength']:.2f}")
        print()
        
        print("风险评估:")
        risk = result['risk_assessment']
        risk_text = {'low': '低风险', 'medium': '中风险', 'high': '高风险'}
        print(f"  综合风险: {risk_text[risk['overall_risk']]}")
        print(f"  波动率风险: {risk_text[risk['volatility_risk']]}")
        print(f"  RSI风险: {risk_text[risk['rsi_risk']]}")
        print()
        
        print("投资建议:")
        print(f"  {result['recommendation']}")
        print()
        
        # 保存分析报告
        filename = f"analysis_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analyzer.save_analysis_report(result, filename)
        print(f"分析报告已保存: {filename}")
        
    except Exception as e:
        print(f"✗ 分析股票失败: {e}")

def analyze_hot_stocks(stock_list):
    """分析热门股票"""
    print("\n正在分析热门股票...")
    print("-" * 40)
    
    try:
        # 选择成交量最大的前10只股票
        hot_stocks = stock_list.nlargest(10, 'volume')['code'].tolist()
        print(f"选择成交量最大的前10只股票: {hot_stocks}")
        print()
        
        # 创建分析器
        analyzer = StockAnalyzer()
        
        # 批量分析
        print("开始批量分析...")
        results = analyzer.batch_analyze(hot_stocks, days=365, prediction_days=5)
        
        # 显示结果摘要
        print("\n批量分析完成！")
        print()
        
        successful_results = [r for r in results if 'error' not in r]
        print(f"成功分析: {len(successful_results)} 只")
        print(f"分析失败: {len(results) - len(successful_results)} 只")
        print()
        
        if successful_results:
            print("分析结果摘要:")
            for result in successful_results:
                print(f"  {result['stock_code']}: {result['recommendation']} "
                      f"(风险: {result['risk_assessment']['overall_risk']})")
            print()
            
            # 生成汇总报告
            summary = analyzer.generate_summary_report(results)
            print("汇总报告:")
            print(summary)
            
            # 保存批量分析报告
            filename = f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            analyzer.save_batch_report(results, filename)
            print(f"\n批量分析报告已保存: {filename}")
        
    except Exception as e:
        print(f"✗ 批量分析失败: {e}")

def analyze_market_sentiment(stock_list):
    """分析市场情绪"""
    print("\n正在分析市场情绪...")
    print("-" * 40)
    
    try:
        # 创建分析器
        analyzer = StockAnalyzer()
        
        # 分析市场情绪
        sentiment = analyzer.analyze_market_sentiment(stock_list, top_n=100)
        
        if 'error' in sentiment:
            print(f"✗ 市场情绪分析失败: {sentiment['error']}")
            return
        
        print("✓ 市场情绪分析完成！")
        print()
        print("市场情绪指标:")
        print(f"  分析股票数量: {sentiment['total_stocks']}")
        print(f"  上涨股票: {sentiment['up_stocks']} 只 ({sentiment['up_ratio']:.1%})")
        print(f"  下跌股票: {sentiment['down_stocks']} 只 ({sentiment['down_ratio']:.1%})")
        print(f"  平盘股票: {sentiment['flat_stocks']} 只")
        print(f"  平均涨跌幅: {sentiment['avg_change']:.2f}%")
        print(f"  平均成交量: {sentiment['avg_volume']:,.0f}")
        print()
        
        # 判断市场情绪
        sentiment_text = {
            'bullish': '看涨',
            'bearish': '看跌',
            'neutral': '震荡'
        }
        print(f"市场情绪: {sentiment_text[sentiment['sentiment']]}")
        
        # 获取主要指数数据
        print("\n正在获取主要指数数据...")
        from stock_data_fetcher import StockDataFetcher
        fetcher = StockDataFetcher()
        indices = fetcher.get_market_index()
        
        if not indices.empty:
            print("主要指数:")
            for _, index in indices.iterrows():
                change_color = "🔴" if index['change_pct'] < 0 else "🟢"
                print(f"  {change_color} {index['name']}: {index['price']:.2f} "
                      f"({index['change_pct']:+.2f}%)")
        
    except Exception as e:
        print(f"✗ 市场情绪分析失败: {e}")

if __name__ == "__main__":
    main()

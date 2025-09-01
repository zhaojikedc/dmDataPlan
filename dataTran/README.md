# 中国股市预测分析系统

## 系统简介

这是一个基于Python的中国股市预测分析系统，集成了数据获取、技术分析、机器学习预测等功能。系统可以从互联网获取实时股票数据，进行技术指标分析，并使用机器学习算法预测股票价格走势。

## 主要功能

### 1. 数据获取
- **股票列表获取**：获取A股市场所有股票的基本信息
- **历史数据获取**：获取指定股票的历史K线数据
- **实时行情**：获取股票的实时价格、成交量等信息
- **财务数据**：获取股票的财务指标数据
- **市场指数**：获取主要市场指数数据
- **行业板块**：获取行业板块涨跌数据

### 2. 技术分析
- **移动平均线**：MA5、MA10、MA20、MA60
- **MACD指标**：MACD线、信号线、柱状图
- **RSI指标**：相对强弱指标
- **布林带**：上轨、中轨、下轨
- **KDJ指标**：随机指标
- **成交量指标**：成交量移动平均
- **支撑阻力位**：自动识别支撑位和阻力位
- **波动率分析**：历史波动率、ATR等

### 3. 机器学习预测
- **多种算法**：随机森林、梯度提升、线性回归、SVM、神经网络等
- **特征工程**：自动创建技术指标特征、滞后特征、统计特征等
- **模型训练**：支持交叉验证、网格搜索优化超参数
- **集成预测**：多模型集成预测，提供置信区间
- **特征重要性**：分析影响预测的关键因素

### 4. 投资建议
- **交易信号**：基于技术指标的综合交易信号
- **风险评估**：多维度风险评估（波动率、RSI、布林带等）
- **投资建议**：结合技术分析和预测结果的智能建议
- **市场情绪**：分析整体市场情绪和趋势

## 系统架构

```
dataTran/
├── stock_predictor.py      # 主程序入口
├── stock_data_fetcher.py   # 数据获取模块
├── technical_analyzer.py   # 技术分析模块
├── ml_predictor.py        # 机器学习预测模块
├── stock_analyzer.py      # 主分析器
├── requirements.txt       # 依赖包列表
└── README.md             # 使用说明
```

## 安装说明

### 1. 环境要求
- Python 3.8+
- Windows/Linux/macOS

### 2. 安装依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 如果TA-Lib安装失败，可以使用conda安装
conda install -c conda-forge ta-lib

# 或者使用预编译包
pip install TA-Lib-binary
```

### 3. 验证安装
```python
python -c "import pandas, numpy, sklearn, talib; print('安装成功！')"
```

## 使用方法

### 1. 基础使用

#### 获取股票列表
```python
from stock_data_fetcher import StockDataFetcher

fetcher = StockDataFetcher()
stock_list = fetcher.get_stock_list()
print(f"获取到 {len(stock_list)} 只股票")
```

#### 获取历史数据
```python
# 获取平安银行的历史数据
history = fetcher.get_stock_history('000001', days=365)
print(history.tail())
```

#### 单只股票分析
```python
from stock_analyzer import StockAnalyzer

analyzer = StockAnalyzer()
result = analyzer.analyze_stock('000001', days=365, prediction_days=5)

print(f"股票代码: {result['stock_code']}")
print(f"当前价格: {result['current_price']:.2f}")
print(f"投资建议: {result['recommendation']}")
print(f"风险评估: {result['risk_assessment']['overall_risk']}")
```

### 2. 批量分析

#### 分析多只股票
```python
stock_codes = ['000001', '000002', '000858', '600036', '600519']
results = analyzer.batch_analyze(stock_codes, days=365, prediction_days=5)

# 生成汇总报告
summary = analyzer.generate_summary_report(results)
print(summary)

# 保存详细报告
analyzer.save_batch_report(results)
```

#### 分析热门股票
```python
# 获取成交量最大的前20只股票
stock_list = fetcher.get_stock_list()
hot_stocks = stock_list.nlargest(20, 'volume')['code'].tolist()
results = analyzer.batch_analyze(hot_stocks)
```

### 3. 市场分析

#### 市场情绪分析
```python
stock_list = fetcher.get_stock_list()
sentiment = analyzer.analyze_market_sentiment(stock_list, top_n=100)
print(f"市场情绪: {sentiment['sentiment']}")
print(f"上涨股票比例: {sentiment['up_ratio']:.2%}")
```

#### 获取市场指数
```python
indices = fetcher.get_market_index()
print(indices)
```

#### 获取行业板块
```python
industries = fetcher.get_industry_data()
print(industries)
```

### 4. 高级功能

#### 自定义技术指标
```python
from technical_analyzer import TechnicalAnalyzer

# 计算自定义指标
data = fetcher.get_stock_history('000001', 100)
indicators = TechnicalAnalyzer.calculate_indicators(data)
signals = TechnicalAnalyzer.generate_signals(indicators)

# 计算支撑阻力位
support_resistance = TechnicalAnalyzer.calculate_support_resistance(data)
print("支撑位:", support_resistance['support'])
print("阻力位:", support_resistance['resistance'])
```

#### 模型训练和预测
```python
from ml_predictor import StockPredictor

predictor = StockPredictor()

# 准备特征数据
X, y = predictor.prepare_features(data, prediction_days=5)

# 训练模型
results = predictor.train_models(X, y, use_grid_search=True)
print("模型性能:", results)

# 进行预测
predictions = predictor.predict(data, prediction_days=5)
print("预测结果:", predictions)

# 保存模型
predictor.save_model('stock_model.pkl')
```

## 配置说明

### 1. 日志配置
系统使用Python标准logging模块，日志文件保存在`stock_predictor.log`中。

### 2. 请求配置
- 请求超时：10秒
- 最大重试次数：3次
- 请求间隔：避免过于频繁的请求

### 3. 模型配置
- 特征选择：自动选择最重要的20个特征
- 交叉验证：5折交叉验证
- 超参数优化：支持网格搜索

## 注意事项

### 1. 数据来源
- 系统使用东方财富网等公开API获取数据
- 数据可能有延迟，不保证实时性
- 建议在非交易时间进行大量数据分析

### 2. 预测准确性
- 机器学习预测基于历史数据，不保证准确性
- 股市有风险，投资需谨慎
- 预测结果仅供参考，不构成投资建议

### 3. 使用限制
- 避免过于频繁的API请求
- 建议使用代理或VPN访问
- 遵守相关网站的使用条款

## 故障排除

### 1. 常见问题

#### TA-Lib安装失败
```bash
# Windows用户
pip install TA-Lib-binary

# Linux用户
sudo apt-get install ta-lib
pip install TA-Lib

# macOS用户
brew install ta-lib
pip install TA-Lib
```

#### 网络请求失败
- 检查网络连接
- 尝试使用代理
- 检查防火墙设置

#### 内存不足
- 减少分析股票数量
- 减少历史数据天数
- 使用更小的特征集

### 2. 性能优化
- 使用多进程处理批量分析
- 缓存常用数据
- 优化特征工程流程

## 扩展开发

### 1. 添加新的技术指标
在`technical_analyzer.py`中添加新的指标计算方法。

### 2. 集成新的机器学习算法
在`ml_predictor.py`中添加新的模型类型。

### 3. 支持新的数据源
在`stock_data_fetcher.py`中添加新的数据获取方法。

### 4. 开发Web界面
可以基于Flask或FastAPI开发Web界面。

## 许可证

本项目仅供学习和研究使用，请勿用于商业用途。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 参与讨论

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础功能实现
- 支持A股市场分析

---

**免责声明**：本系统仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。使用者应自行承担使用本系统的一切风险和责任。









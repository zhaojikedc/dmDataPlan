#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习预测器模块
使用机器学习算法进行股票价格预测
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

# 机器学习相关
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression

logger = logging.getLogger(__name__)

class StockPredictor:
    """股票预测器"""
    
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression(),
            'svr': SVR(kernel='rbf', C=1.0, gamma='scale'),
            'mlp': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        }
        
        self.scaler = StandardScaler()
        self.feature_selector = SelectKBest(score_func=f_regression, k=20)
        self.trained_models = {}
        self.best_model = None
        
    def prepare_features(self, df: pd.DataFrame, prediction_days: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """准备特征数据"""
        try:
            # 选择基础特征列 - 使用technical_analyzer.py中生成的列名
            feature_columns = [
                'open', 'high', 'low', 'close', 'volume',
                'ma5', 'ma10', 'ma20', 'ma60',
                'macd', 'macd_signal', 'macd_histogram',
                'rsi', 'bb_upper', 'bb_middle', 'bb_lower',
                'kdj_k', 'kdj_d', 'kdj_j',
                'volume_ma5', 'volume_ma20', 'momentum', 'williams_r'
            ]
            
            # 检查哪些列存在
            available_columns = [col for col in feature_columns if col in df.columns]
            
            if len(available_columns) < 5:
                logger.warning(f"可用特征列太少: {available_columns}")
                # 使用基本的OHLCV数据
                available_columns = ['open', 'high', 'low', 'close', 'volume']
            
            # 创建滞后特征
            for col in ['close', 'volume']:
                if col in df.columns:
                    for lag in [1, 2, 3, 5]:
                        df[f'{col}_lag_{lag}'] = df[col].shift(lag)
            
            # 创建移动平均特征
            for col in ['close', 'volume']:
                if col in df.columns:
                    for window in [3, 5, 10, 20]:
                        df[f'{col}_ma_{window}'] = df[col].rolling(window=window).mean()
                        df[f'{col}_std_{window}'] = df[col].rolling(window=window).std()
            
            # 创建价格变化特征
            if 'close' in df.columns:
                df['price_change'] = df['close'].pct_change()
                df['price_change_2'] = df['close'].pct_change(2)
                df['price_change_5'] = df['close'].pct_change(5)
            
            # 创建波动率特征
            if 'close' in df.columns:
                df['volatility'] = df['close'].rolling(window=20).std()
                df['volatility_5'] = df['close'].rolling(window=5).std()
            
            # 创建技术指标比率
            if 'ma5' in df.columns and 'ma20' in df.columns:
                df['ma_ratio_5_20'] = df['ma5'] / df['ma20']
            if 'ma10' in df.columns and 'ma60' in df.columns:
                df['ma_ratio_10_60'] = df['ma10'] / df['ma60']
            if 'bb_upper' in df.columns and 'bb_lower' in df.columns and 'close' in df.columns:
                df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # 创建成交量特征
            if 'volume' in df.columns and 'volume_ma5' in df.columns:
                df['volume_ratio'] = df['volume'] / df['volume_ma5']
                df['volume_change'] = df['volume'].pct_change()
            
            # 创建价格动量特征
            if 'close' in df.columns:
                df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
                df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
            
            # 添加所有可用的技术指标
            for col in df.columns:
                if col not in available_columns and col not in ['date', 'index']:
                    available_columns.append(col)
            
            # 准备特征矩阵
            feature_data = df[available_columns].copy()
            
            # 处理缺失值
            feature_data = feature_data.fillna(method='ffill').fillna(method='bfill').fillna(0)
            
            # 创建目标变量（未来N天的价格）
            if 'close' in feature_data.columns:
                target = feature_data['close'].shift(-prediction_days)
                # 移除最后几行（没有目标值）
                feature_data = feature_data.iloc[:-prediction_days]
                target = target.iloc[:-prediction_days]
                
                # 确保数据长度一致
                min_length = min(len(feature_data), len(target))
                feature_data = feature_data.iloc[:min_length]
                target = target.iloc[:min_length]
                
                # 转换为numpy数组
                X = feature_data.values
                y = target.values
                
                logger.info(f"特征准备完成: X形状={X.shape}, y形状={y.shape}")
                return X, y
            else:
                logger.error("没有找到收盘价列")
                return np.array([]), np.array([])
                
        except Exception as e:
            logger.error(f"准备特征数据失败: {e}")
            return np.array([]), np.array([])
    
    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """训练模型"""
        try:
            if X.size == 0 or y.size == 0:
                logger.error("特征或目标数据为空")
                return {}
            
            # 分割训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 缩放特征
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            trained_models = {}
            results = {}
            
            # 训练所有模型
            for name, model in self.models.items():
                logger.info(f"训练模型: {name}")
                
                try:
                    # 训练模型
                    model.fit(X_train_scaled, y_train)
                    
                    # 预测
                    y_pred = model.predict(X_test_scaled)
                    
                    # 评估模型
                    mse = mean_squared_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    
                    # 交叉验证
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
                    
                    results[name] = {
                        'mse': mse,
                        'r2': r2,
                        'cv_mean': cv_scores.mean(),
                        'cv_std': cv_scores.std(),
                        'rmse': np.sqrt(mse)
                    }
                    
                    trained_models[name] = model
                    
                    logger.info(f"{name} 模型训练完成 - R²: {r2:.4f}, CV: {cv_scores.mean():.4f}±{cv_scores.std():.4f}")
                    
                except Exception as e:
                    logger.error(f"训练模型 {name} 失败: {e}")
                    results[name] = {'error': str(e)}
            
            self.trained_models = trained_models
            
            # 选择最佳模型
            best_model_name = max(results.keys(), key=lambda k: results[k].get('cv_mean', -np.inf) if 'error' not in results[k] else -np.inf)
            if 'error' not in results[best_model_name]:
                self.best_model = trained_models[best_model_name]
                logger.info(f"选择最佳模型: {best_model_name}")
            
            return results
            
        except Exception as e:
            logger.error(f"训练模型失败: {e}")
            return {}
    
    def predict(self, df: pd.DataFrame, prediction_days: int = 5) -> pd.DataFrame:
        """进行预测"""
        try:
            if not self.trained_models:
                raise ValueError("模型未训练，请先调用train_models方法")
            
            if not self.scaler:
                raise ValueError("缩放器未初始化")
            
            # 准备最新特征
            latest_features = df.iloc[-1:].copy()
            
            # 准备特征
            X_latest, _ = self.prepare_features(latest_features, prediction_days)
            
            if X_latest.size == 0:
                raise ValueError("无法准备预测特征")
            
            # 缩放特征
            X_latest_scaled = self.scaler.transform(X_latest)
            
            predictions = {}
            
            # 使用每个模型进行预测
            for name, model in self.trained_models.items():
                try:
                    pred = model.predict(X_latest_scaled)
                    predictions[name] = pred[0]
                except Exception as e:
                    logger.error(f"模型 {name} 预测失败: {e}")
                    predictions[name] = None
            
            # 过滤掉预测失败的模型
            valid_predictions = {k: v for k, v in predictions.items() if v is not None}
            
            if not valid_predictions:
                raise ValueError("所有模型预测都失败了")
            
            # 计算集成预测
            ensemble_pred = np.mean(list(valid_predictions.values()))
            
            # 计算预测置信区间
            pred_std = np.std(list(valid_predictions.values()))
            confidence_interval = 1.96 * pred_std  # 95%置信区间
            
            # 创建预测结果
            pred_dates = pd.date_range(
                start=df.index[-1] + timedelta(days=1),
                periods=prediction_days,
                freq='D'
            )
            
            pred_df = pd.DataFrame({
                'date': pred_dates,
                'ensemble_prediction': ensemble_pred,
                'prediction_std': pred_std,
                'confidence_upper': ensemble_pred + confidence_interval,
                'confidence_lower': ensemble_pred - confidence_interval,
                **{f'{name}_prediction': pred for name, pred in valid_predictions.items()}
            })
            
            pred_df.set_index('date', inplace=True)
            
            logger.info(f"预测完成，未来{prediction_days}天预测价格: {ensemble_pred:.2f} ± {confidence_interval:.2f}")
            return pred_df
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            return pd.DataFrame()
    
    def get_feature_importance(self) -> pd.DataFrame:
        """获取特征重要性"""
        try:
            if not self.best_model or not hasattr(self.best_model, 'feature_importances_'):
                return pd.DataFrame()
            
            # 获取特征名称
            feature_names = [f'feature_{i}' for i in range(len(self.best_model.feature_importances_))]
            
            # 创建特征重要性DataFrame
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': self.best_model.feature_importances_
            })
            
            # 按重要性排序
            importance_df = importance_df.sort_values('importance', ascending=False)
            
            return importance_df
            
        except Exception as e:
            logger.error(f"获取特征重要性失败: {e}")
            return pd.DataFrame()
    
    def save_model(self, filepath: str):
        """保存模型"""
        try:
            import joblib
            
            model_data = {
                'models': self.trained_models,
                'best_model': self.best_model,
                'scaler': self.scaler,
                'feature_selector': self.feature_selector
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"模型已保存到: {filepath}")
            
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
    
    def load_model(self, filepath: str):
        """加载模型"""
        try:
            import joblib
            
            model_data = joblib.load(filepath)
            
            self.trained_models = model_data['models']
            self.best_model = model_data['best_model']
            self.scaler = model_data['scaler']
            self.feature_selector = model_data['feature_selector']
            
            logger.info(f"模型已从 {filepath} 加载")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")

if __name__ == "__main__":
    predictor = StockPredictor()
    print("股票预测器初始化成功")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本依赖测试脚本
检查核心模块是否可用
"""

import sys
import os

def test_imports():
    """测试基本模块导入"""
    print("=" * 50)
    print("测试基本模块导入")
    print("=" * 50)
    
    # 测试核心模块
    modules = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('sklearn', 'sklearn'),
        ('requests', 'requests'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('datetime', 'datetime'),
        ('json', 'json'),
        ('logging', 'logging')
    ]
    
    success_count = 0
    total_count = len(modules)
    
    for module_name, import_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name} - 导入成功")
            success_count += 1
        except ImportError as e:
            print(f"✗ {module_name} - 导入失败: {e}")
    
    print(f"\n导入结果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("✓ 所有核心模块导入成功！")
        return True
    else:
        print("✗ 部分模块导入失败，请安装缺失的依赖")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "=" * 50)
    print("测试基本功能")
    print("=" * 50)
    
    try:
        import pandas as pd
        import numpy as np
        
        # 创建测试数据
        data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=10),
            'price': np.random.randn(10).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 10)
        })
        
        print("✓ 创建测试数据成功")
        print(f"  数据形状: {data.shape}")
        print(f"  列名: {list(data.columns)}")
        
        # 测试基本计算
        data['returns'] = data['price'].pct_change()
        data['ma5'] = data['price'].rolling(5).mean()
        
        print("✓ 基本计算功能正常")
        print(f"  最新价格: {data['price'].iloc[-1]:.2f}")
        print(f"  5日均价: {data['ma5'].iloc[-1]:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("中国股市预测系统 - 基本功能测试")
    print("=" * 50)
    
    # 测试模块导入
    import_success = test_imports()
    
    if import_success:
        # 测试基本功能
        func_success = test_basic_functionality()
        
        if func_success:
            print("\n" + "=" * 50)
            print("🎉 所有测试通过！系统可以正常运行")
            print("=" * 50)
            
            print("\n下一步:")
            print("1. 运行 python quick_start.py 启动完整系统")
            print("2. 或运行 python start_simple.py 启动英文版本")
        else:
            print("\n基本功能测试失败，请检查系统配置")
    else:
        print("\n请先安装缺失的依赖:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()









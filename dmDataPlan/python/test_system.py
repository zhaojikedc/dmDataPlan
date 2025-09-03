#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统功能测试脚本
"""

import json
import os
import sys
from data_handler import DataHandler

def test_data_handler():
    """测试数据处理器"""
    print("=" * 50)
    print("测试数据处理器功能")
    print("=" * 50)
    
    handler = DataHandler()
    
    # 测试1: 加载现有数据
    print("1. 测试加载现有数据...")
    app_data = handler.load_json_data("app_management.json")
    print(f"   加载的应用数据: {len(app_data.get('applications', []))} 条")
    
    # 测试2: 添加新数据
    print("2. 测试添加新数据...")
    new_app = {
        "name": "测试应用",
        "owner": "测试用户",
        "status": "active",
        "themes": ["test_theme"],
        "description": "这是一个测试应用"
    }
    
    success = handler.add_item("app_management.json", "applications", new_app)
    print(f"   添加结果: {'成功' if success else '失败'}")
    
    # 测试3: 获取统计信息
    print("3. 测试获取统计信息...")
    stats = handler.get_file_stats("app_management.json")
    print(f"   统计信息: {stats}")
    
    # 测试4: 搜索数据
    print("4. 测试搜索数据...")
    results = handler.search_items("app_management.json", "applications", "name", "测试")
    print(f"   搜索结果: {len(results)} 条")
    
    # 测试5: 列出所有数据
    print("5. 测试列出所有数据...")
    all_items = handler.list_items("app_management.json", "applications")
    print(f"   所有应用: {len(all_items)} 条")
    
    print("数据处理器测试完成！")

def test_json_files():
    """测试JSON文件格式"""
    print("\n" + "=" * 50)
    print("测试JSON文件格式")
    print("=" * 50)
    
    config_dir = "../config"
    json_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
    
    for filename in json_files:
        filepath = os.path.join(config_dir, filename)
        print(f"检查文件: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"  ✓ JSON格式正确")
                print(f"  ✓ 包含 {len(data)} 个顶级键")
                
                # 检查数据结构
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"  ✓ {key}: {len(value)} 个项目")
                    else:
                        print(f"  ✓ {key}: {type(value).__name__}")
                        
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON格式错误: {e}")
        except Exception as e:
            print(f"  ✗ 读取文件失败: {e}")
    
    print("JSON文件测试完成！")

def test_api_endpoints():
    """测试API端点（需要服务器运行）"""
    print("\n" + "=" * 50)
    print("测试API端点")
    print("=" * 50)
    
    try:
        from api_client import APIClient
        
        client = APIClient()
        
        # 测试获取数据
        print("1. 测试获取数据...")
        data = client.get_data("app_management.json")
        print(f"   获取数据: {'成功' if data else '失败'}")
        
        # 测试获取统计信息
        print("2. 测试获取统计信息...")
        stats = client.get_stats("app_management.json")
        print(f"   统计信息: {'成功' if stats else '失败'}")
        
    except Exception as e:
        print(f"API测试失败（服务器可能未运行）: {e}")
        print("请先启动Web服务器: python start_server.py")

def main():
    """主测试函数"""
    print("数据交互系统功能测试")
    print("=" * 60)
    
    # 切换到脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        # 运行测试
        test_data_handler()
        test_json_files()
        test_api_endpoints()
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


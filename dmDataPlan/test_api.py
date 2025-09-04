#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API端点
"""

import requests
import json

def test_save_selected_tables():
    """测试保存已选表API"""
    try:
        # 测试数据
        test_data = {
            "title": "测试已选表信息",
            "description": "测试API保存功能",
            "tables": [
                {
                    "name": "test_table_1",
                    "type": "fact",
                    "fields": [
                        {
                            "key": "id",
                            "type": "string",
                            "pk": True,
                            "fk": False,
                            "cn": "主键"
                        }
                    ]
                }
            ],
            "selectedTableNames": ["test_table_1"],
            "last_updated": "2025-01-02T10:00:00.000Z"
        }
        
        print("正在测试API端点...")
        print("测试数据:", json.dumps(test_data, indent=2, ensure_ascii=False))
        
        # 发送POST请求
        response = requests.post(
            'http://localhost:8080/api/save-selected-tables',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ API调用成功！")
            return True
        else:
            print("❌ API调用失败！")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：服务器可能没有运行")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_get_selected_tables():
    """测试获取已选表API"""
    try:
        print("\n正在测试获取API...")
        response = requests.get('http://localhost:8080/api/data?file=selected_tables.json', timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取API成功！")
            print("文件内容:", json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print("❌ 获取API失败！")
            return False
            
    except Exception as e:
        print(f"❌ 获取测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== API端点测试 ===")
    
    # 测试保存API
    save_success = test_save_selected_tables()
    
    # 测试获取API
    get_success = test_get_selected_tables()
    
    print(f"\n=== 测试结果 ===")
    print(f"保存API: {'✅ 成功' if save_success else '❌ 失败'}")
    print(f"获取API: {'✅ 成功' if get_success else '❌ 失败'}")

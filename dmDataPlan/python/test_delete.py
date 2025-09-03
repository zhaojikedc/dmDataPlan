#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试删除功能脚本
"""

import requests
import json
import time

def test_delete_function():
    """测试删除功能"""
    base_url = "http://localhost:8080"
    
    print("=" * 50)
    print("测试删除功能")
    print("=" * 50)
    
    # 1. 获取当前数据
    print("1. 获取当前应用数据...")
    try:
        response = requests.get(f"{base_url}/api/data?file=app_management.json&type=applications")
        if response.status_code == 200:
            data = response.json()
            print(f"   当前有 {len(data)} 个应用:")
            for app in data:
                print(f"   - ID: {app.get('id')}, 名称: {app.get('name')}")
        else:
            print(f"   获取数据失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   连接失败: {e}")
        return
    
    if len(data) == 0:
        print("   没有数据可以删除")
        return
    
    # 2. 删除第一个应用
    app_to_delete = data[0]
    app_id = app_to_delete.get('id')
    app_name = app_to_delete.get('name')
    
    print(f"\n2. 删除应用: {app_name} (ID: {app_id})")
    try:
        response = requests.delete(f"{base_url}/api/data/app_management.json/applications/{app_id}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✓ 删除成功")
            else:
                print("   ✗ 删除失败")
                return
        else:
            print(f"   ✗ 删除失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ 删除失败: {e}")
        return
    
    # 3. 验证删除结果
    print("\n3. 验证删除结果...")
    time.sleep(1)  # 等待1秒
    try:
        response = requests.get(f"{base_url}/api/data?file=app_management.json&type=applications")
        if response.status_code == 200:
            new_data = response.json()
            print(f"   删除后还有 {len(new_data)} 个应用:")
            for app in new_data:
                print(f"   - ID: {app.get('id')}, 名称: {app.get('name')}")
            
            # 检查删除的应用是否还在
            deleted_app_exists = any(app.get('id') == app_id for app in new_data)
            if deleted_app_exists:
                print("   ✗ 删除失败：应用仍然存在")
            else:
                print("   ✓ 删除成功：应用已不存在")
        else:
            print(f"   验证失败: {response.status_code}")
    except Exception as e:
        print(f"   验证失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_delete_function()


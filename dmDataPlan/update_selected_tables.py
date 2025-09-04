#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新selected_tables.json文件的脚本
"""

import json
import os
import sys
from datetime import datetime

def update_selected_tables(selected_tables_data):
    """更新selected_tables.json文件"""
    try:
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(script_dir, 'config')
        file_path = os.path.join(config_dir, 'selected_tables.json')
        
        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        # 更新数据
        data = {
            "title": "已选表信息",
            "description": "用户在模型关系创建页面选择的表信息",
            "tables": selected_tables_data.get('tables', []),
            "selectedTableNames": selected_tables_data.get('selectedTableNames', []),
            "last_updated": datetime.now().isoformat() + "Z"
        }
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已选表信息已更新到: {file_path}")
        print(f"📊 包含 {len(data['selectedTableNames'])} 个已选表")
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python update_selected_tables.py <JSON数据>")
        print("示例: python update_selected_tables.py '{\"selectedTableNames\":[\"table1\"]}'")
        return
    
    try:
        # 解析命令行参数
        json_data = json.loads(sys.argv[1])
        success = update_selected_tables(json_data)
        
        if success:
            print("🎉 更新成功！")
        else:
            print("💥 更新失败！")
            sys.exit(1)
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

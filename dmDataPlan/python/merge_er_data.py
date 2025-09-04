#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O线ER关系数据合并脚本
合并selected_tables.json和o_line_relations.json文件
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

def load_json_file(file_path: str) -> Optional[Dict]:
    """加载JSON文件"""
    try:
        if not os.path.exists(file_path):
            print(f"警告: 文件不存在 {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"成功加载文件: {file_path}")
            return data
    except Exception as e:
        print(f"加载文件失败 {file_path}: {e}")
        return None

def get_table_from_selected_tables(table_name: str, selected_tables_data: Dict) -> Optional[Dict]:
    """从selected_tables.json中获取表的完整信息（包含完整字段信息）"""
    if not selected_tables_data or 'tables' not in selected_tables_data:
        return None
        
    for table in selected_tables_data['tables']:
        if table.get('name') == table_name:
            return table
    return None

def get_table_metadata(table_name: str, table_metadata: Dict) -> Optional[Dict]:
    """从table_metadata中获取表的完整信息"""
    if not table_metadata or 'tables' not in table_metadata:
        return None
        
    for table in table_metadata['tables']:
        if table.get('name') == table_name:
            return table
    return None

def merge_er_data(selected_tables_path: str, relations_path: str, table_metadata_path: str, output_path: str) -> bool:
    """合并ER数据"""
    try:
        print("开始合并ER数据...")
        
        # 加载数据文件
        selected_tables_data = load_json_file(selected_tables_path)
        relations_data = load_json_file(relations_path)
        table_metadata = load_json_file(table_metadata_path)
        
        if not selected_tables_data:
            print("错误: 无法加载selected_tables.json")
            return False
            
        if not relations_data:
            print("错误: 无法加载o_line_relations.json")
            return False
            
        if not table_metadata:
            print("错误: 无法加载table_metadata.json")
            return False
        
        # 获取已选表名列表
        selected_table_names = []
        if 'selectedTableNames' in selected_tables_data:
            selected_table_names = selected_tables_data['selectedTableNames']
        elif 'selectedTables' in selected_tables_data:
            selected_table_names = selected_tables_data['selectedTables']
        elif isinstance(selected_tables_data, list) and len(selected_tables_data) > 0:
            # 如果是数组格式，取最后一个元素
            last_item = selected_tables_data[-1]
            if 'selectedTableNames' in last_item:
                selected_table_names = last_item['selectedTableNames']
            elif 'selectedTables' in last_item:
                selected_table_names = last_item['selectedTables']
        
        print(f"已选表数量: {len(selected_table_names)}")
        print(f"已选表列表: {selected_table_names}")
        
        # 获取关系数据
        relations = []
        if 'relations' in relations_data:
            relations = relations_data['relations']
        elif isinstance(relations_data, list):
            relations = relations_data
        
        print(f"关系数量: {len(relations)}")
        
        # 构建合并后的表信息
        merged_tables = []
        for table_name in selected_table_names:
            # 优先从selected_tables.json中获取表信息（包含完整字段信息）
            table_info = get_table_from_selected_tables(table_name, selected_tables_data)
            if table_info:
                merged_tables.append(table_info)
                print(f"从selected_tables.json找到表信息: {table_name}")
            else:
                # 如果selected_tables.json中没有，尝试从table_metadata.json获取
                table_info = get_table_metadata(table_name, table_metadata)
                if table_info:
                    merged_tables.append(table_info)
                    print(f"从table_metadata.json找到表信息: {table_name}")
                else:
                    print(f"警告: 未找到表信息 {table_name}")
                    # 创建一个基本的表信息
                    basic_table_info = {
                        "name": table_name,
                        "type": "unknown",
                        "description": f"表 {table_name}",
                        "fields": []
                    }
                    merged_tables.append(basic_table_info)
        
        # 构建合并后的数据
        merged_data = {
            "title": "O线ER关系图",
            "description": "本图展示了系统数据库的实体关系模型，包括事实表和维度表及其关联关系。",
            "tables": merged_tables,
            "relations": relations,
            "textBoxes": [],
            "collapseStates": {},
            "metadata": {
                "mergeTime": datetime.now().isoformat(),
                "selectedTablesCount": len(selected_table_names),
                "relationsCount": len(relations),
                "sourceFiles": {
                    "selectedTables": selected_tables_path,
                    "relations": relations_path,
                    "tableMetadata": table_metadata_path
                }
            }
        }
        
        # 初始化折叠状态
        for table in merged_tables:
            table_name = table.get('name', '')
            if table_name:
                merged_data['collapseStates'][table_name] = True
        
        # 保存合并后的数据
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        print(f"数据合并完成，保存到: {output_path}")
        print(f"合并结果:")
        print(f"  - 表数量: {len(merged_tables)}")
        print(f"  - 关系数量: {len(relations)}")
        print(f"  - 合并时间: {merged_data['metadata']['mergeTime']}")
        
        return True
        
    except Exception as e:
        print(f"合并数据失败: {e}")
        return False

def main():
    """主函数"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 配置文件路径
    config_dir = os.path.join(os.path.dirname(script_dir), 'config')
    selected_tables_path = os.path.join(config_dir, 'selected_tables.json')
    relations_path = os.path.join(config_dir, 'o_line_relations.json')
    table_metadata_path = os.path.join(config_dir, 'table_metadata.json')
    output_path = os.path.join(config_dir, 'merged_er_data.json')
    
    print("O线ER关系数据合并脚本")
    print("=" * 50)
    print(f"已选表文件: {selected_tables_path}")
    print(f"关系文件: {relations_path}")
    print(f"表元数据文件: {table_metadata_path}")
    print(f"输出文件: {output_path}")
    print("=" * 50)
    
    # 执行合并
    success = merge_er_data(selected_tables_path, relations_path, table_metadata_path, output_path)
    
    if success:
        print("\n✅ 数据合并成功!")
        sys.exit(0)
    else:
        print("\n❌ 数据合并失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()

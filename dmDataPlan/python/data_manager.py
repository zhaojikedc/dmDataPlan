#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理命令行工具
提供命令行接口用于管理JSON数据文件
"""

import argparse
import json
import sys
from data_handler import DataHandler

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据管理命令行工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加数据命令
    add_parser = subparsers.add_parser('add', help='添加数据项')
    add_parser.add_argument('file', help='JSON文件名')
    add_parser.add_argument('type', help='数据类型')
    add_parser.add_argument('--name', required=True, help='项目名称')
    add_parser.add_argument('--owner', help='负责人')
    add_parser.add_argument('--status', default='active', help='状态')
    add_parser.add_argument('--description', help='描述')
    
    # 删除数据命令
    delete_parser = subparsers.add_parser('delete', help='删除数据项')
    delete_parser.add_argument('file', help='JSON文件名')
    delete_parser.add_argument('type', help='数据类型')
    delete_parser.add_argument('id', help='项目ID')
    
    # 列出数据命令
    list_parser = subparsers.add_parser('list', help='列出数据项')
    list_parser.add_argument('file', help='JSON文件名')
    list_parser.add_argument('type', help='数据类型')
    
    # 获取统计信息命令
    stats_parser = subparsers.add_parser('stats', help='获取统计信息')
    stats_parser.add_argument('file', help='JSON文件名')
    
    # 搜索数据命令
    search_parser = subparsers.add_parser('search', help='搜索数据项')
    search_parser.add_argument('file', help='JSON文件名')
    search_parser.add_argument('type', help='数据类型')
    search_parser.add_argument('key', help='搜索字段')
    search_parser.add_argument('value', help='搜索值')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化数据处理器
    handler = DataHandler()
    
    try:
        if args.command == 'add':
            # 添加数据项
            item_data = {
                'name': args.name,
                'owner': args.owner,
                'status': args.status,
                'description': args.description
            }
            
            # 移除None值
            item_data = {k: v for k, v in item_data.items() if v is not None}
            
            success = handler.add_item(args.file, args.type, item_data)
            if success:
                print(f"成功添加数据项到 {args.file}")
            else:
                print(f"添加数据项失败")
                sys.exit(1)
                
        elif args.command == 'delete':
            # 删除数据项
            success = handler.delete_item(args.file, args.type, args.id)
            if success:
                print(f"成功删除数据项 {args.id}")
            else:
                print(f"删除数据项失败")
                sys.exit(1)
                
        elif args.command == 'list':
            # 列出数据项
            items = handler.list_items(args.file, args.type)
            if items:
                print(f"{args.file} - {args.type} 数据项:")
                print("-" * 50)
                for item in items:
                    print(f"ID: {item.get('id', 'N/A')}")
                    print(f"名称: {item.get('name', 'N/A')}")
                    print(f"负责人: {item.get('owner', 'N/A')}")
                    print(f"状态: {item.get('status', 'N/A')}")
                    if item.get('description'):
                        print(f"描述: {item.get('description')}")
                    print("-" * 50)
            else:
                print(f"未找到 {args.type} 类型的数据项")
                
        elif args.command == 'stats':
            # 获取统计信息
            stats = handler.get_file_stats(args.file)
            print(f"文件统计信息: {args.file}")
            print("-" * 50)
            print(f"最后更新: {stats.get('last_updated', 'N/A')}")
            print(f"总项目数: {stats.get('total_items', 0)}")
            print("各类型项目数:")
            for item_type, count in stats.get('item_types', {}).items():
                print(f"  {item_type}: {count}")
                
        elif args.command == 'search':
            # 搜索数据项
            results = handler.search_items(args.file, args.type, args.key, args.value)
            if results:
                print(f"搜索结果 ({len(results)} 条):")
                print("-" * 50)
                for item in results:
                    print(f"ID: {item.get('id', 'N/A')}")
                    print(f"名称: {item.get('name', 'N/A')}")
                    print(f"负责人: {item.get('owner', 'N/A')}")
                    print(f"状态: {item.get('status', 'N/A')}")
                    print("-" * 50)
            else:
                print(f"未找到匹配的数据项")
                
    except Exception as e:
        print(f"操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


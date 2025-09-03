#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动Web服务器脚本
"""

import sys
import os
import argparse
from web_server import start_server

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='启动数据交互Web服务器')
    parser.add_argument('--host', default='localhost', help='服务器主机地址 (默认: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口 (默认: 8080)')
    parser.add_argument('--config-dir', default='../config', help='配置文件目录 (默认: ../config)')
    
    args = parser.parse_args()
    
    # 切换到脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("=" * 60)
    print("数据仓库数据模型管理系统 - Web服务器")
    print("=" * 60)
    print(f"服务器地址: http://{args.host}:{args.port}")
    print(f"配置文件目录: {args.config_dir}")
    print("=" * 60)
    print("API端点:")
    print("  GET  /api/data?file=filename&type=item_type - 获取数据")
    print("  GET  /api/data/filename/type/id - 获取特定项目")
    print("  GET  /api/stats?file=filename - 获取统计信息")
    print("  POST /api/data - 添加数据")
    print("  POST /api/data/filename/type/id - 更新数据")
    print("  DELETE /api/data/filename/type/id - 删除数据")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        start_server(args.host, args.port)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


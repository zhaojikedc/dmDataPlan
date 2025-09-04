#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试合并脚本的编码问题
"""

import subprocess
import sys
import os

def test_merge_script():
    """测试合并脚本"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    merge_script = os.path.join(script_dir, 'python', 'merge_er_data.py')
    
    print(f"测试脚本: {merge_script}")
    print(f"脚本存在: {os.path.exists(merge_script)}")
    
    # 设置环境变量确保UTF-8编码
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        # 执行合并脚本
        result = subprocess.run([sys.executable, merge_script], 
                              capture_output=True, text=True, 
                              encoding='utf-8', errors='replace',
                              env=env)
        
        print(f"返回码: {result.returncode}")
        print(f"标准输出: {result.stdout}")
        print(f"标准错误: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ 合并脚本执行成功!")
        else:
            print("❌ 合并脚本执行失败!")
            
    except Exception as e:
        print(f"执行异常: {e}")

if __name__ == "__main__":
    test_merge_script()

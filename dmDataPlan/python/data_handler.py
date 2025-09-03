#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据交互处理模块
用于处理HTML页面与JSON数据文件的交互
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataHandler:
    """数据处理器类"""
    
    def __init__(self, config_dir: str = None):
        """
        初始化数据处理器
        
        Args:
            config_dir: JSON配置文件目录
        """
        if config_dir is None:
            # 默认使用上级目录的config文件夹
            self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        else:
            self.config_dir = config_dir
        self.ensure_config_dir()
    
    def ensure_config_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            logger.info(f"创建配置目录: {self.config_dir}")
    
    def load_json_data(self, filename: str) -> Dict[str, Any]:
        """
        加载JSON数据文件
        
        Args:
            filename: JSON文件名
            
        Returns:
            解析后的JSON数据
        """
        filepath = os.path.join(self.config_dir, filename)
        
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"成功加载JSON文件: {filename}")
                    return data
            else:
                logger.warning(f"JSON文件不存在: {filename}")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON文件格式错误 {filename}: {e}")
            return {}
        except Exception as e:
            logger.error(f"加载JSON文件失败 {filename}: {e}")
            return {}
    
    def save_json_data(self, filename: str, data: Dict[str, Any]) -> bool:
        """
        保存数据到JSON文件
        
        Args:
            filename: JSON文件名
            data: 要保存的数据
            
        Returns:
            保存是否成功
        """
        filepath = os.path.join(self.config_dir, filename)
        
        try:
            # 添加时间戳
            if isinstance(data, dict):
                data['last_updated'] = datetime.now().isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功保存JSON文件: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存JSON文件失败 {filename}: {e}")
            return False
    
    def add_item(self, filename: str, item_type: str, item_data: Dict[str, Any]) -> bool:
        """
        添加新项目到JSON文件
        
        Args:
            filename: JSON文件名
            item_type: 项目类型（如applications, themes等）
            item_data: 项目数据
            
        Returns:
            添加是否成功
        """
        data = self.load_json_data(filename)
        
        if item_type not in data:
            data[item_type] = []
        
        # 生成唯一ID
        if 'id' not in item_data:
            item_data['id'] = f"{item_type}_{uuid.uuid4().hex[:8]}"
        
        # 添加创建时间
        item_data['created_at'] = datetime.now().isoformat()
        
        data[item_type].append(item_data)
        
        return self.save_json_data(filename, data)
    
    def update_item(self, filename: str, item_type: str, item_id: str, update_data: Dict[str, Any]) -> bool:
        """
        更新JSON文件中的项目
        
        Args:
            filename: JSON文件名
            item_type: 项目类型
            item_id: 项目ID
            update_data: 更新数据
            
        Returns:
            更新是否成功
        """
        data = self.load_json_data(filename)
        
        if item_type not in data:
            logger.error(f"项目类型不存在: {item_type}")
            return False
        
        # 查找并更新项目
        for i, item in enumerate(data[item_type]):
            if item.get('id') == item_id:
                # 保留原有字段，更新新字段
                data[item_type][i].update(update_data)
                data[item_type][i]['updated_at'] = datetime.now().isoformat()
                return self.save_json_data(filename, data)
        
        logger.error(f"未找到ID为 {item_id} 的项目")
        return False
    
    def delete_item(self, filename: str, item_type: str, item_id: str) -> bool:
        """
        从JSON文件中删除项目
        
        Args:
            filename: JSON文件名
            item_type: 项目类型
            item_id: 项目ID
            
        Returns:
            删除是否成功
        """
        data = self.load_json_data(filename)
        
        if item_type not in data:
            logger.error(f"项目类型不存在: {item_type}")
            return False
        
        # 查找并删除项目
        original_length = len(data[item_type])
        data[item_type] = [item for item in data[item_type] if item.get('id') != item_id]
        
        if len(data[item_type]) < original_length:
            logger.info(f"成功删除项目: {item_id}")
            return self.save_json_data(filename, data)
        else:
            logger.error(f"未找到ID为 {item_id} 的项目")
            return False
    
    def get_item_by_id(self, filename: str, item_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取项目
        
        Args:
            filename: JSON文件名
            item_type: 项目类型
            item_id: 项目ID
            
        Returns:
            项目数据或None
        """
        data = self.load_json_data(filename)
        
        if item_type not in data:
            return None
        
        for item in data[item_type]:
            if item.get('id') == item_id:
                return item
        
        return None
    
    def list_items(self, filename: str, item_type: str) -> List[Dict[str, Any]]:
        """
        列出指定类型的所有项目
        
        Args:
            filename: JSON文件名
            item_type: 项目类型
            
        Returns:
            项目列表
        """
        data = self.load_json_data(filename)
        return data.get(item_type, [])
    
    def search_items(self, filename: str, item_type: str, search_key: str, search_value: str) -> List[Dict[str, Any]]:
        """
        搜索项目
        
        Args:
            filename: JSON文件名
            item_type: 项目类型
            search_key: 搜索字段
            search_value: 搜索值
            
        Returns:
            匹配的项目列表
        """
        items = self.list_items(filename, item_type)
        return [item for item in items if search_value.lower() in str(item.get(search_key, '')).lower()]
    
    def get_file_stats(self, filename: str) -> Dict[str, Any]:
        """
        获取文件统计信息
        
        Args:
            filename: JSON文件名
            
        Returns:
            统计信息
        """
        data = self.load_json_data(filename)
        stats = {
            'filename': filename,
            'last_updated': data.get('last_updated', 'Unknown'),
            'total_items': 0,
            'item_types': {}
        }
        
        for key, value in data.items():
            if key != 'last_updated' and isinstance(value, list):
                stats['item_types'][key] = len(value)
                stats['total_items'] += len(value)
        
        return stats

# 创建全局数据处理器实例
data_handler = DataHandler()

# 便捷函数
def load_data(filename: str) -> Dict[str, Any]:
    """加载JSON数据"""
    return data_handler.load_json_data(filename)

def save_data(filename: str, data: Dict[str, Any]) -> bool:
    """保存JSON数据"""
    return data_handler.save_json_data(filename, data)

def add_item(filename: str, item_type: str, item_data: Dict[str, Any]) -> bool:
    """添加项目"""
    return data_handler.add_item(filename, item_type, item_data)

def update_item(filename: str, item_type: str, item_id: str, update_data: Dict[str, Any]) -> bool:
    """更新项目"""
    return data_handler.update_item(filename, item_type, item_id, update_data)

def delete_item(filename: str, item_type: str, item_id: str) -> bool:
    """删除项目"""
    return data_handler.delete_item(filename, item_type, item_id)

def get_item(filename: str, item_type: str, item_id: str) -> Optional[Dict[str, Any]]:
    """获取项目"""
    return data_handler.get_item_by_id(filename, item_type, item_id)

def list_items(filename: str, item_type: str) -> List[Dict[str, Any]]:
    """列出项目"""
    return data_handler.list_items(filename, item_type)

if __name__ == "__main__":
    # 测试代码
    handler = DataHandler()
    
    # 测试加载数据
    app_data = handler.load_json_data("app_management.json")
    print("应用管理数据:", app_data)
    
    # 测试添加数据
    new_app = {
        "name": "Test Application",
        "owner": "test_user",
        "status": "active",
        "themes": ["theme_test"]
    }
    
    success = handler.add_item("app_management.json", "applications", new_app)
    print(f"添加应用: {'成功' if success else '失败'}")
    
    # 测试获取统计信息
    stats = handler.get_file_stats("app_management.json")
    print("文件统计:", stats)

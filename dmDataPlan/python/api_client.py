#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API客户端模块
提供Python客户端接口用于与Web API交互
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIClient:
    """API客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        初始化API客户端
        
        Args:
            base_url: API服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_data(self, filename: str, item_type: str = None) -> Dict[str, Any]:
        """
        获取数据
        
        Args:
            filename: JSON文件名
            item_type: 项目类型（可选）
            
        Returns:
            数据字典
        """
        params = {'file': filename}
        if item_type:
            params['type'] = item_type
        
        try:
            response = self.session.get(f"{self.base_url}/api/data", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"获取数据失败: {e}")
            return {}
    
    def get_item(self, filename: str, item_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        获取特定项目
        
        Args:
            filename: JSON文件名
            item_type: 项目类型
            item_id: 项目ID
            
        Returns:
            项目数据或None
        """
        try:
            response = self.session.get(f"{self.base_url}/api/data/{filename}/{item_type}/{item_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"获取项目失败: {e}")
            return None
    
    def add_item(self, filename: str, item_type: str, item_data: Dict[str, Any]) -> bool:
        """
        添加项目
        
        Args:
            filename: JSON文件名
            item_type: 项目类型
            item_data: 项目数据
            
        Returns:
            是否成功
        """
        data = {
            'filename': filename,
            'type': item_type,
            'data': item_data
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/data", json=data)
            response.raise_for_status()
            result = response.json()
            return result.get('success', False)
        except requests.exceptions.RequestException as e:
            logger.error(f"添加项目失败: {e}")
            return False
    
    def update_item(self, filename: str, item_type: str, item_id: str, update_data: Dict[str, Any]) -> bool:
        """
        更新项目
        
        Args:
            filename: JSON文件名
            item_type: 项目类型
            item_id: 项目ID
            update_data: 更新数据
            
        Returns:
            是否成功
        """
        try:
            response = self.session.post(f"{self.base_url}/api/data/{filename}/{item_type}/{item_id}", json=update_data)
            response.raise_for_status()
            result = response.json()
            return result.get('success', False)
        except requests.exceptions.RequestException as e:
            logger.error(f"更新项目失败: {e}")
            return False
    
    def delete_item(self, filename: str, item_type: str, item_id: str) -> bool:
        """
        删除项目
        
        Args:
            filename: JSON文件名
            item_type: 项目类型
            item_id: 项目ID
            
        Returns:
            是否成功
        """
        try:
            response = self.session.delete(f"{self.base_url}/api/data/{filename}/{item_type}/{item_id}")
            response.raise_for_status()
            result = response.json()
            return result.get('success', False)
        except requests.exceptions.RequestException as e:
            logger.error(f"删除项目失败: {e}")
            return False
    
    def get_stats(self, filename: str) -> Dict[str, Any]:
        """
        获取文件统计信息
        
        Args:
            filename: JSON文件名
            
        Returns:
            统计信息
        """
        try:
            response = self.session.get(f"{self.base_url}/api/stats", params={'file': filename})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def list_items(self, filename: str, item_type: str) -> List[Dict[str, Any]]:
        """
        列出指定类型的所有项目
        
        Args:
            filename: JSON文件名
            item_type: 项目类型
            
        Returns:
            项目列表
        """
        data = self.get_data(filename, item_type)
        return data if isinstance(data, list) else []
    
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

# 便捷函数
def create_client(base_url: str = "http://localhost:8080") -> APIClient:
    """创建API客户端实例"""
    return APIClient(base_url)

# 全局客户端实例
default_client = APIClient()

def get_data(filename: str, item_type: str = None) -> Dict[str, Any]:
    """获取数据"""
    return default_client.get_data(filename, item_type)

def get_item(filename: str, item_type: str, item_id: str) -> Optional[Dict[str, Any]]:
    """获取项目"""
    return default_client.get_item(filename, item_type, item_id)

def add_item(filename: str, item_type: str, item_data: Dict[str, Any]) -> bool:
    """添加项目"""
    return default_client.add_item(filename, item_type, item_data)

def update_item(filename: str, item_type: str, item_id: str, update_data: Dict[str, Any]) -> bool:
    """更新项目"""
    return default_client.update_item(filename, item_type, item_id, update_data)

def delete_item(filename: str, item_type: str, item_id: str) -> bool:
    """删除项目"""
    return default_client.delete_item(filename, item_type, item_id)

def get_stats(filename: str) -> Dict[str, Any]:
    """获取统计信息"""
    return default_client.get_stats(filename)

def list_items(filename: str, item_type: str) -> List[Dict[str, Any]]:
    """列出项目"""
    return default_client.list_items(filename, item_type)

if __name__ == "__main__":
    # 测试代码
    client = APIClient()
    
    # 测试获取数据
    try:
        app_data = client.get_data("app_management.json")
        print("应用管理数据:", app_data)
        
        # 测试添加数据
        new_app = {
            "name": "Test Application via API",
            "owner": "api_test_user",
            "status": "active",
            "themes": ["theme_test"]
        }
        
        success = client.add_item("app_management.json", "applications", new_app)
        print(f"添加应用: {'成功' if success else '失败'}")
        
        # 测试获取统计信息
        stats = client.get_stats("app_management.json")
        print("文件统计:", stats)
        
    except Exception as e:
        print(f"API测试失败，请确保Web服务器正在运行: {e}")


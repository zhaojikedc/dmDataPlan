#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据仓库数据模型管理系统 - CRUD操作脚本
支持主题管理、数据标准、数据规范的增删改查操作
使用JSON作为后端数据存储
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dmDataPlan.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataManager:
    """数据管理器基类"""
    
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.data = []
        self.load_data()
    
    def load_data(self):
        """从JSON文件加载数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"从 {self.data_file} 加载了 {len(self.data)} 条数据")
            else:
                self.data = []
                logger.info(f"数据文件 {self.data_file} 不存在，创建空数据列表")
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            self.data = []
    
    def save_data(self):
        """保存数据到JSON文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存到 {self.data_file}")
            return True
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            return False
    
    def get_all(self) -> List[Dict]:
        """获取所有数据"""
        return self.data
    
    def get_by_id(self, item_id: int) -> Optional[Dict]:
        """根据ID获取数据"""
        for item in self.data:
            if item.get('id') == item_id:
                return item
        return None
    
    def create(self, item_data: Dict) -> Optional[Dict]:
        """创建新数据"""
        try:
            # 生成新ID
            new_id = max([item.get('id', 0) for item in self.data], default=0) + 1
            
            # 添加创建时间和ID
            item_data['id'] = new_id
            item_data['createTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item_data['updateTime'] = item_data['createTime']
            
            self.data.append(item_data)
            
            if self.save_data():
                logger.info(f"创建数据成功，ID: {new_id}")
                return item_data
            else:
                logger.error("保存数据失败")
                return None
        except Exception as e:
            logger.error(f"创建数据失败: {e}")
            return None
    
    def update(self, item_id: int, update_data: Dict) -> Optional[Dict]:
        """更新数据"""
        try:
            item = self.get_by_id(item_id)
            if not item:
                logger.warning(f"未找到ID为 {item_id} 的数据")
                return None
            
            # 更新数据
            for key, value in update_data.items():
                if key != 'id':  # 不允许修改ID
                    item[key] = value
            
            # 更新时间
            item['updateTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if self.save_data():
                logger.info(f"更新数据成功，ID: {item_id}")
                return item
            else:
                logger.error("保存数据失败")
                return None
        except Exception as e:
            logger.error(f"更新数据失败: {e}")
            return None
    
    def delete(self, item_id: int) -> bool:
        """删除数据"""
        try:
            item = self.get_by_id(item_id)
            if not item:
                logger.warning(f"未找到ID为 {item_id} 的数据")
                return False
            
            self.data = [item for item in self.data if item.get('id') != item_id]
            
            if self.save_data():
                logger.info(f"删除数据成功，ID: {item_id}")
                return True
            else:
                logger.error("保存数据失败")
                return False
        except Exception as e:
            logger.error(f"删除数据失败: {e}")
            return False
    
    def search(self, search_term: str, fields: List[str]) -> List[Dict]:
        """搜索数据"""
        try:
            search_term = search_term.lower()
            results = []
            
            for item in self.data:
                for field in fields:
                    if field in item and str(item[field]).lower().find(search_term) != -1:
                        results.append(item)
                        break
            
            logger.info(f"搜索 '{search_term}' 找到 {len(results)} 条结果")
            return results
        except Exception as e:
            logger.error(f"搜索数据失败: {e}")
            return []

class ThemeManager(DataManager):
    """主题管理器"""
    
    def __init__(self):
        super().__init__('data/themes.json')
        self.init_default_data()
    
    def init_default_data(self):
        """初始化默认主题数据"""
        if not self.data:
            default_themes = [
                {
                    "code": "CUSTOMER",
                    "name": "客户主题",
                    "description": "客户相关的所有数据，包括客户基本信息、交易记录等",
                    "status": "active"
                },
                {
                    "code": "PRODUCT",
                    "name": "产品主题",
                    "description": "产品相关的所有数据，包括产品信息、库存、价格等",
                    "status": "active"
                },
                {
                    "code": "ORDER",
                    "name": "订单主题",
                    "description": "订单相关的所有数据，包括订单信息、支付记录等",
                    "status": "active"
                }
            ]
            
            for theme in default_themes:
                self.create(theme)
    
    def search_themes(self, search_term: str) -> List[Dict]:
        """搜索主题"""
        return self.search(search_term, ['name', 'description', 'code'])
    
    def get_active_themes(self) -> List[Dict]:
        """获取启用的主题"""
        return [theme for theme in self.data if theme.get('status') == 'active']

class DataStandardManager(DataManager):
    """数据标准管理器"""
    
    def __init__(self):
        super().__init__('data/standards.json')
        self.init_default_data()
    
    def init_default_data(self):
        """初始化默认数据标准"""
        if not self.data:
            default_standards = [
                {
                    "code": "CUSTOMER_ID",
                    "name": "客户ID",
                    "type": "string",
                    "dataType": "VARCHAR",
                    "lengthPrecision": "32",
                    "isRequired": True,
                    "description": "客户唯一标识符",
                    "status": "active"
                },
                {
                    "code": "CUSTOMER_NAME",
                    "name": "客户姓名",
                    "type": "string",
                    "dataType": "VARCHAR",
                    "lengthPrecision": "100",
                    "isRequired": True,
                    "description": "客户真实姓名",
                    "status": "active"
                },
                {
                    "code": "AMOUNT",
                    "name": "金额",
                    "type": "decimal",
                    "dataType": "DECIMAL",
                    "lengthPrecision": "15,2",
                    "isRequired": True,
                    "description": "交易金额，保留两位小数",
                    "status": "active"
                }
            ]
            
            for standard in default_standards:
                self.create(standard)
    
    def search_standards(self, search_term: str) -> List[Dict]:
        """搜索数据标准"""
        return self.search(search_term, ['name', 'description', 'code'])
    
    def get_standards_by_type(self, standard_type: str) -> List[Dict]:
        """根据类型获取数据标准"""
        return [standard for standard in self.data if standard.get('type') == standard_type]
    
    def get_active_standards(self) -> List[Dict]:
        """获取启用的数据标准"""
        return [standard for standard in self.data if standard.get('status') == 'active']

class DataSpecificationManager(DataManager):
    """数据规范管理器"""
    
    def __init__(self):
        super().__init__('data/specifications.json')
        self.init_default_data()
    
    def init_default_data(self):
        """初始化默认数据规范"""
        if not self.data:
            default_specifications = [
                {
                    "code": "NAMING_RULE_001",
                    "name": "表命名规范",
                    "type": "naming",
                    "businessDomain": "customer",
                    "owner": "张三",
                    "version": "1.0",
                    "description": "数据表命名必须遵循特定规则，包括前缀、业务域标识等",
                    "status": "active"
                },
                {
                    "code": "STRUCTURE_RULE_001",
                    "name": "字段结构规范",
                    "type": "structure",
                    "businessDomain": "product",
                    "owner": "李四",
                    "version": "1.0",
                    "description": "数据字段必须包含标准属性，如创建时间、更新时间、创建人等",
                    "status": "active"
                },
                {
                    "code": "QUALITY_RULE_001",
                    "name": "数据质量规范",
                    "type": "quality",
                    "businessDomain": "order",
                    "owner": "王五",
                    "version": "1.0",
                    "description": "数据必须满足完整性、准确性、一致性等质量要求",
                    "status": "active"
                }
            ]
            
            for spec in default_specifications:
                self.create(spec)
    
    def search_specifications(self, search_term: str) -> List[Dict]:
        """搜索数据规范"""
        return self.search(search_term, ['name', 'description', 'code', 'owner'])
    
    def get_specifications_by_type(self, spec_type: str) -> List[Dict]:
        """根据类型获取数据规范"""
        return [spec for spec in self.data if spec.get('type') == spec_type]
    
    def get_specifications_by_domain(self, business_domain: str) -> List[Dict]:
        """根据业务域获取数据规范"""
        return [spec for spec in self.data if spec.get('businessDomain') == business_domain]

def main():
    """主函数 - 演示CRUD操作"""
    print("数据仓库数据模型管理系统 - CRUD操作演示")
    print("=" * 50)
    
    # 初始化管理器
    theme_manager = ThemeManager()
    standard_manager = DataStandardManager()
    spec_manager = DataSpecificationManager()
    
    # 演示主题管理
    print("\n1. 主题管理演示")
    print("-" * 30)
    
    # 创建新主题
    new_theme = {
        "code": "FINANCE",
        "name": "财务主题",
        "description": "财务相关的所有数据，包括收入、支出、利润等",
        "status": "active"
    }
    
    created_theme = theme_manager.create(new_theme)
    if created_theme:
        print(f"创建主题成功: {created_theme['name']}")
    
    # 搜索主题
    search_results = theme_manager.search_themes("客户")
    print(f"搜索'客户'找到 {len(search_results)} 个主题")
    
    # 获取所有主题
    all_themes = theme_manager.get_all()
    print(f"总共有 {len(all_themes)} 个主题")
    
    # 演示数据标准管理
    print("\n2. 数据标准管理演示")
    print("-" * 30)
    
    # 创建新标准
    new_standard = {
        "code": "EMAIL",
        "name": "邮箱地址",
        "type": "string",
        "dataType": "VARCHAR",
        "lengthPrecision": "255",
        "isRequired": False,
        "description": "电子邮箱地址",
        "status": "active"
    }
    
    created_standard = standard_manager.create(new_standard)
    if created_standard:
        print(f"创建数据标准成功: {created_standard['name']}")
    
    # 搜索标准
    search_results = standard_manager.search_standards("客户")
    print(f"搜索'客户'找到 {len(search_results)} 个标准")
    
    # 演示数据规范管理
    print("\n3. 数据规范管理演示")
    print("-" * 30)
    
    # 创建新规范
    new_spec = {
        "code": "SECURITY_RULE_001",
        "name": "数据安全规范",
        "type": "security",
        "businessDomain": "finance",
        "owner": "赵六",
        "version": "1.0",
        "description": "确保数据安全性和隐私保护的规范要求",
        "status": "active"
    }
    
    created_spec = spec_manager.create(new_spec)
    if created_spec:
        print(f"创建数据规范成功: {created_spec['name']}")
    
    # 搜索规范
    search_results = spec_manager.search_specifications("安全")
    print(f"搜索'安全'找到 {len(search_results)} 个规范")
    
    print("\nCRUD操作演示完成！")
    print("数据已保存到 data/ 目录下的JSON文件中")

if __name__ == "__main__":
    main()

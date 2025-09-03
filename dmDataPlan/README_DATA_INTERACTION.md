# 数据交互系统说明文档

## 概述

本系统为dmDataPlan项目提供了完整的HTML页面与JSON数据文件的动态交互功能。通过Python Web服务器和JavaScript API客户端，实现了数据的增删改查操作。

## 系统架构

```
dmDataPlan/
├── config/                 # JSON数据文件目录
│   ├── app_management.json
│   ├── theme_management.json
│   ├── data_standards.json
│   └── data_specifications.json
├── html/                   # HTML页面目录
│   ├── js/
│   │   └── data-api.js     # JavaScript API客户端
│   ├── app_management_dynamic.html  # 动态数据加载示例页面
│   └── ...                 # 其他HTML页面
└── python/                 # Python后端服务
    ├── data_handler.py     # 数据处理器
    ├── web_server.py       # Web服务器
    ├── api_client.py       # Python API客户端
    ├── start_server.py     # 服务器启动脚本
    └── data_manager.py     # 命令行数据管理工具
```

## 功能特性

### 1. 数据管理功能
- ✅ 动态加载JSON数据
- ✅ 添加新数据项
- ✅ 更新现有数据
- ✅ 删除数据项
- ✅ 搜索和过滤数据
- ✅ 分页显示
- ✅ 实时数据同步

### 2. API接口
- `GET /api/data` - 获取数据
- `GET /api/data/{filename}/{type}/{id}` - 获取特定项目
- `GET /api/stats` - 获取统计信息
- `POST /api/data` - 添加数据
- `POST /api/data/{filename}/{type}/{id}` - 更新数据
- `DELETE /api/data/{filename}/{type}/{id}` - 删除数据

### 3. 支持的JSON文件格式
```json
{
  "applications": [
    {
      "id": "app_001",
      "name": "应用名称",
      "owner": "负责人",
      "status": "active",
      "themes": ["theme1", "theme2"],
      "description": "应用描述",
      "created_at": "2025-01-01T00:00:00",
      "updated_at": "2025-01-01T00:00:00"
    }
  ],
  "last_updated": "2025-01-01T00:00:00"
}
```

## 快速开始

### 1. 启动Web服务器

```bash
# 进入python目录
cd dmDataPlan/python

# 启动服务器（默认端口8080）
python start_server.py

# 自定义端口和主机
python start_server.py --host 0.0.0.0 --port 9000
```

### 2. 访问动态页面

打开浏览器访问：
- 动态应用管理页面：`http://localhost:8080/../html/app_management_dynamic.html`

### 3. 使用命令行工具

```bash
# 添加数据项
python data_manager.py add app_management.json applications --name "新应用" --owner "张三"

# 列出数据项
python data_manager.py list app_management.json applications

# 删除数据项
python data_manager.py delete app_management.json applications app_001

# 搜索数据项
python data_manager.py search app_management.json applications name "应用"

# 获取统计信息
python data_manager.py stats app_management.json
```

## 使用方法

### 1. 在HTML页面中集成

```html
<!-- 引入API库 -->
<script src="js/data-api.js"></script>

<script>
// 初始化数据表格
initDataTable('tableId', 'filename.json', 'dataType');

// 添加数据
async function addItem() {
    const success = await dataAPI.addItem('app_management.json', 'applications', {
        name: '新应用',
        owner: '张三',
        status: 'active'
    });
}

// 删除数据
async function deleteItem(id) {
    const success = await dataAPI.deleteItem('app_management.json', 'applications', id);
}
</script>
```

### 2. 在Python中使用API客户端

```python
from api_client import APIClient

# 创建客户端
client = APIClient('http://localhost:8080')

# 获取数据
data = client.get_data('app_management.json', 'applications')

# 添加数据
success = client.add_item('app_management.json', 'applications', {
    'name': '新应用',
    'owner': '张三',
    'status': 'active'
})

# 删除数据
success = client.delete_item('app_management.json', 'applications', 'item_id')
```

## 配置说明

### 1. 服务器配置
- 默认主机：localhost
- 默认端口：8080
- 配置文件目录：../config

### 2. 数据文件配置
- 支持UTF-8编码
- 自动添加时间戳
- 自动生成唯一ID

### 3. 跨域配置
- 支持CORS跨域请求
- 允许所有来源访问（开发环境）

## 错误处理

### 1. 常见错误
- 文件不存在：返回空数据
- JSON格式错误：记录错误日志
- 网络连接失败：显示错误提示

### 2. 错误日志
- 服务器端：控制台输出
- 客户端：浏览器控制台

## 扩展开发

### 1. 添加新的数据类型
1. 在config目录创建新的JSON文件
2. 定义数据结构
3. 在HTML页面中添加对应的表格和表单

### 2. 自定义API端点
1. 修改web_server.py
2. 添加新的路由处理函数
3. 更新JavaScript API客户端

### 3. 添加数据验证
1. 在data_handler.py中添加验证函数
2. 在API接口中调用验证
3. 返回详细的错误信息

## 注意事项

1. **数据备份**：修改前请备份JSON文件
2. **并发访问**：当前版本不支持并发写入
3. **文件权限**：确保Python进程有读写权限
4. **网络访问**：生产环境请配置防火墙规则

## 故障排除

### 1. 服务器启动失败
- 检查端口是否被占用
- 确认Python版本兼容性
- 检查文件权限

### 2. 数据加载失败
- 检查JSON文件格式
- 确认文件路径正确
- 查看服务器日志

### 3. 页面显示异常
- 检查浏览器控制台错误
- 确认API服务器运行状态
- 验证网络连接

## 更新日志

- v1.0.0: 初始版本，支持基本的CRUD操作
- 支持动态数据加载和实时更新
- 提供命令行管理工具
- 完整的错误处理和日志记录


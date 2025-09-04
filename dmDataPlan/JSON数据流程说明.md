# JSON数据流程说明

## 功能概述

实现了基于JSON文件的完整数据流程，从表元数据到ER关系图的自动生成。整个流程分为四个步骤，确保数据的完整性和一致性。

## 数据流程架构

### 1. 表元数据JSON文件 (`config/table_metadata.json`)
- **作用**: 存储所有数据库表的完整结构信息
- **内容**: 表名、数据库、类型、字段信息（字段名、类型、主键、外键、中文名等）
- **特点**: 静态数据，包含完整的表结构定义

### 2. 关系创建页面 (`o_line_management.html`)
- **功能**: 从表元数据JSON文件读取表信息，用户选择表和创建关系
- **操作**: 选择数据库 → 选择表 → 创建表关系 → 生成两个JSON文件
- **输出**: 表信息JSON + 关系信息JSON

### 3. ER关系图页面 (`o_erGenHtml.html`)
- **功能**: 合并两个JSON文件，生成完整的ER图数据并渲染
- **输入**: 表信息JSON + 关系信息JSON
- **输出**: 完整的ER关系图

## 详细实现

### 表元数据结构
```json
{
  "title": "O线数据表元数据",
  "description": "包含所有数据库表的完整结构信息",
  "tables": [
    {
      "name": "dim.dim_tp_air_full_cargo_di",
      "database": "dim",
      "type": "dim",
      "description": "航空全货机维度表",
      "fields": [
        {
          "key": "flight_date",
          "type": "string",
          "pk": true,
          "fk": false,
          "cn": "航班日期"
        }
      ]
    }
  ]
}
```

### 表信息JSON结构
```json
{
  "title": "O线数据表信息",
  "description": "基于关系创建页面选择的表信息",
  "tables": [
    {
      "name": "dim.dim_tp_air_full_cargo_di",
      "database": "dim",
      "type": "dim",
      "description": "航空全货机维度表",
      "fields": [...]
    }
  ],
  "selectedTables": ["dim.dim_tp_air_full_cargo_di"],
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### 关系信息JSON结构
```json
{
  "title": "O线数据关系信息",
  "description": "基于关系创建页面创建的表关系信息",
  "relations": [
    {
      "sourceTable": "dm_tp.dm_tp_air_flow_weight_sum_di",
      "targetTable": "dim.dim_tp_air_full_cargo_di",
      "sourceField": "flight_no",
      "targetField": "cpct_name",
      "relationType": "one-to-one",
      "isFactDim": "是",
      "createTime": "2024-01-01 00:00:00"
    }
  ],
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### 合并后的ER图数据结构
```json
{
  "title": "O线ER关系图",
  "description": "基于关系创建页面的数据自动生成",
  "tables": [...],
  "relations": [
    {
      "source": "dm_tp.dm_tp_air_flow_weight_sum_di",
      "target": "dim.dim_tp_air_full_cargo_di",
      "type": "one-to-one",
      "sourceField": "flight_no",
      "targetField": "cpct_name",
      "isFactDim": true
    }
  ]
}
```

## 使用方法

### 步骤1: 准备表元数据
1. 编辑 `config/table_metadata.json` 文件
2. 添加所有需要的表结构信息
3. 确保字段信息完整（字段名、类型、主键、外键、中文名）

### 步骤2: 在关系创建页面操作
1. 打开 `o_line_management.html` 页面
2. 选择数据库（从表元数据中自动获取）
3. 选择需要的表（从表元数据中过滤）
4. 创建表关系
5. 点击"生成表信息JSON"和"生成关系信息JSON"按钮

### 步骤3: 查看ER关系图
1. 切换到"O线ER关系说明"标签页
2. ER图会自动显示合并后的数据
3. 点击"刷新数据"按钮重新加载最新数据

### 步骤4: 数据管理
1. 使用"导出完整数据"按钮保存所有数据
2. 使用"导入数据"按钮恢复数据
3. 使用"手动同步"按钮确保数据一致性

## 关键函数说明

### 关系创建页面
- `loadTables()`: 从表元数据JSON文件加载表信息
- `generateTableInfoJSON()`: 生成表信息JSON文件
- `generateRelationInfoJSON()`: 生成关系信息JSON文件
- `saveDataToStorage()`: 保存数据到localStorage

### ER关系图页面
- `loadDataFromJSONFiles()`: 从JSON文件加载数据并合并
- `loadDataFromStorage()`: 从localStorage加载数据
- `reinitializeData()`: 重新初始化ER图数据

## 测试页面

### 数据同步测试页面 (`test_sync.html`)
- 测试localStorage数据同步功能
- 验证表选择和关系创建的数据流转

### JSON数据流程测试页面 (`test_json_flow.html`)
- 测试完整的JSON数据流程
- 模拟从表元数据到ER图的完整过程
- 验证数据格式和转换逻辑

## 技术特点

1. **数据完整性**: 从表元数据到ER图的完整数据链路
2. **格式标准化**: 统一的JSON数据格式
3. **实时同步**: localStorage + JSON文件的混合存储
4. **错误处理**: 完善的异常处理机制
5. **用户友好**: 直观的操作界面和状态提示

## 注意事项

1. **文件路径**: 确保表元数据JSON文件路径正确
2. **数据格式**: 表元数据JSON必须符合指定格式
3. **浏览器兼容性**: 需要支持fetch API的现代浏览器
4. **数据一致性**: 表名在关系创建和ER图中必须一致

## 故障排除

### 表元数据加载失败
1. 检查 `config/table_metadata.json` 文件是否存在
2. 验证JSON格式是否正确
3. 确认文件路径是否正确

### 表选择不显示
1. 检查表元数据中是否有对应数据库的表
2. 验证数据库名称是否匹配
3. 查看浏览器控制台错误信息

### ER图不显示
1. 确认关系创建页面有数据
2. 检查localStorage中是否有完整数据
3. 尝试点击"刷新数据"按钮

### JSON文件生成失败
1. 确认已选择表
2. 检查浏览器是否支持文件下载
3. 查看控制台错误信息

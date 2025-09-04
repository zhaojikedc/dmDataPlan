# JSON数据增强功能说明

## 功能概述

基于用户需求，对JSON数据流程进行了增强，实现了从表元数据JSON文件到动态下拉列表的完整数据链路，以及表选择和关系JSON文件的生成与查看功能。

## 新增功能

### 1. 动态数据库下拉列表
- **功能**: 从表元数据JSON文件中自动提取数据库信息
- **实现**: `initDatabaseSelect()` 函数
- **特点**: 
  - 自动获取所有唯一的数据库名称
  - 动态生成下拉列表选项
  - 支持多数据库环境

### 2. 动态表下拉列表
- **功能**: 根据选择的数据库，从表元数据中过滤并显示对应的表列表
- **实现**: 修改了 `loadTables()` 函数
- **特点**:
  - 基于选择的数据库过滤表
  - 显示表的完整信息
  - 支持表搜索和选择

### 3. 表选择JSON生成
- **功能**: 通过表选择功能，生成包含选中表完整结构信息的JSON文件
- **实现**: `generateTableInfoJSON()` 函数
- **特点**:
  - 包含选中表的完整字段信息
  - 自动下载JSON文件
  - 支持批量表选择

### 4. 关系JSON查看功能
- **功能**: 提供查看当前表关系JSON数据的功能
- **实现**: `viewRelationJSON()` 函数
- **特点**:
  - 在新窗口中预览JSON数据
  - 显示关系统计信息
  - 支持格式化显示

## 技术实现

### 数据流程
```
表元数据JSON文件 → 动态数据库下拉列表 → 动态表下拉列表 → 表选择 → JSON文件生成
```

### 关键函数

#### 1. `loadTableMetadata()`
```javascript
async function loadTableMetadata() {
    // 加载表元数据JSON文件
    // 初始化数据库下拉列表
}
```

#### 2. `initDatabaseSelect()`
```javascript
function initDatabaseSelect() {
    // 从表元数据中提取数据库信息
    // 动态生成数据库下拉列表选项
}
```

#### 3. `generateTableInfoJSON()`
```javascript
async function generateTableInfoJSON() {
    // 过滤已选择的表
    // 生成表信息JSON文件
    // 自动下载文件
}
```

#### 4. `viewRelationJSON()`
```javascript
function viewRelationJSON() {
    // 在新窗口中显示关系JSON数据
    // 格式化显示和统计信息
}
```

## 使用方法

### 步骤1: 页面加载
1. 打开 `o_line_management.html` 页面
2. 系统自动加载表元数据JSON文件
3. 数据库下拉列表自动填充

### 步骤2: 选择数据库和表
1. 从数据库下拉列表中选择数据库
2. 表列表自动更新显示对应数据库的表
3. 选择需要的表

### 步骤3: 生成表信息JSON
1. 点击"生成表信息JSON"按钮
2. 系统自动生成包含选中表完整结构的JSON文件
3. 文件自动下载到本地

### 步骤4: 创建表关系
1. 在右侧面板创建表关系
2. 关系数据自动保存到localStorage

### 步骤5: 查看关系JSON
1. 点击"查看关系JSON"按钮
2. 在新窗口中预览关系JSON数据
3. 点击"生成关系信息JSON"按钮下载文件

## 数据格式

### 表信息JSON格式
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

### 关系信息JSON格式
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

## 测试页面

### 1. JSON数据增强功能测试页面 (`test_json_enhancement.html`)
- 测试动态数据库下拉列表功能
- 测试表选择JSON生成功能
- 测试关系JSON查看功能
- 模拟完整的表选择和关系创建流程

### 2. JSON数据流程测试页面 (`test_json_flow.html`)
- 测试完整的JSON数据流程
- 验证数据格式和转换逻辑

## 技术特点

1. **动态数据加载**: 从JSON文件动态加载数据库和表信息
2. **实时数据同步**: 表选择和关系创建实时同步到localStorage
3. **文件自动下载**: 支持JSON文件自动下载功能
4. **数据预览**: 支持在新窗口中预览JSON数据
5. **错误处理**: 完善的异常处理和用户提示

## 注意事项

1. **文件路径**: 确保表元数据JSON文件路径正确
2. **数据格式**: 表元数据JSON必须符合指定格式
3. **浏览器兼容性**: 需要支持fetch API和Blob API的现代浏览器
4. **数据一致性**: 表名在关系创建和ER图中必须一致

## 故障排除

### 数据库下拉列表为空
1. 检查表元数据JSON文件是否存在
2. 验证JSON格式是否正确
3. 查看浏览器控制台错误信息

### 表列表不显示
1. 确认已选择数据库
2. 检查表元数据中是否有对应数据库的表
3. 验证数据库名称是否匹配

### JSON文件生成失败
1. 确认已选择表或创建关系
2. 检查浏览器是否支持文件下载
3. 查看控制台错误信息

### 关系JSON查看失败
1. 确认已创建表关系
2. 检查浏览器弹窗是否被阻止
3. 查看控制台错误信息

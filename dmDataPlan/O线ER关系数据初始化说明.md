# O线ER关系数据初始化说明

## 概述

根据O线ER关系图的关系，我们已经为新增关系页面初始化了一版示例数据。这些关系数据基于表元数据中的表结构，创建了合理的表间关联关系。

## 完成的工作

### 1. 创建了关系数据文件

**文件位置**: `dmDataPlan/config/o_line_er_models.json`

**内容**: 包含10条示例关系数据，涵盖了所有主要表之间的关联关系。

### 2. 创建了初始化页面

**文件位置**: `dmDataPlan/html/init_relations.html`

**功能**:
- 查看当前关系数据
- 初始化示例关系数据
- 同步到关系创建页面
- 验证数据完整性

### 3. 增强了关系创建页面

**文件位置**: `dmDataPlan/html/o_line_management.html`

**新增功能**:
- 添加了"初始化示例关系"按钮
- 实现了`initSampleRelations()`函数
- 自动加载和显示示例关系数据

## 初始化的关系数据

### 关系列表

1. **航空全货机维度表与流向配置关系**
   - 源表: `dim.dim_tp_air_full_cargo_di`
   - 目标表: `dm_pass_atp.tm_air_flow_config_wide`
   - 关系: `deprt_city_code` -> `src_city_code`
   - 类型: 1:N

2. **航空全货机维度表与流向配置关系2**
   - 源表: `dim.dim_tp_air_full_cargo_di`
   - 目标表: `dm_pass_atp.tm_air_flow_config_wide`
   - 关系: `arrive_city_code` -> `dest_city_code`
   - 类型: 1:N

3. **流向配置与流向重量汇总关系**
   - 源表: `dm_pass_atp.tm_air_flow_config_wide`
   - 目标表: `dm_tp.dm_tp_air_flow_weight_sum_di`
   - 关系: `city_flow` -> `flight_flow`
   - 类型: 1:N

4. **流向重量汇总与全流向汇总关系**
   - 源表: `dm_tp.dm_tp_air_flow_weight_sum_di`
   - 目标表: `dm_tp.dm_tp_air_full_flow_sum_di`
   - 关系: `flight_task_id` -> `send_flight_task_id`
   - 类型: 1:1

5. **全流向汇总与时效达成汇总关系**
   - 源表: `dm_tp.dm_tp_air_full_flow_sum_di`
   - 目标表: `dm_tp.dm_tp_air_full_time_achieve_sum_di`
   - 关系: `flight_flow` -> `flight_flow`
   - 类型: 1:N

6. **时效达成汇总与价格明细关系**
   - 源表: `dm_tp.dm_tp_air_full_time_achieve_sum_di`
   - 目标表: `dm_tp.dm_tp_air_get_price_dtl_di`
   - 关系: `src_city_code` -> `depart_city_code`
   - 类型: 1:N

7. **时效达成汇总与价格明细关系2**
   - 源表: `dm_tp.dm_tp_air_full_time_achieve_sum_di`
   - 目标表: `dm_tp.dm_tp_air_get_price_dtl_di`
   - 关系: `dest_city_code` -> `arrive_city_code`
   - 类型: 1:N

8. **航空全货机维度表与流向重量汇总关系**
   - 源表: `dim.dim_tp_air_full_cargo_di`
   - 目标表: `dm_tp.dm_tp_air_flow_weight_sum_di`
   - 关系: `cpct_name` -> `flight_no`
   - 类型: 1:N

9. **流向配置与时效达成汇总关系**
   - 源表: `dm_pass_atp.tm_air_flow_config_wide`
   - 目标表: `dm_tp.dm_tp_air_full_time_achieve_sum_di`
   - 关系: `src_city_code` -> `src_city_code`
   - 类型: 1:N

10. **流向配置与时效达成汇总关系2**
    - 源表: `dm_pass_atp.tm_air_flow_config_wide`
    - 目标表: `dm_tp.dm_tp_air_full_time_achieve_sum_di`
    - 关系: `dest_city_code` -> `dest_city_code`
    - 类型: 1:N

## 使用方法

### 方法1: 通过关系创建页面初始化

1. 打开 `http://localhost:8080/html/o_line_management.html`
2. 点击"初始化示例关系"按钮
3. 确认覆盖现有数据（如果有的话）
4. 系统会自动创建10条示例关系数据

### 方法2: 通过初始化页面

1. 打开 `http://localhost:8080/html/init_relations.html`
2. 点击"初始化示例关系"按钮
3. 点击"同步到关系创建页面"按钮
4. 验证数据完整性

## 数据特点

### 关系类型分布
- **1:N关系**: 8条（一对多关系）
- **1:1关系**: 2条（一对一关系）

### 表类型覆盖
- **维度表**: `dim.dim_tp_air_full_cargo_di`
- **配置表**: `dm_pass_atp.tm_air_flow_config_wide`
- **事实表**: 
  - `dm_tp.dm_tp_air_flow_weight_sum_di`
  - `dm_tp.dm_tp_air_full_flow_sum_di`
  - `dm_tp.dm_tp_air_full_time_achieve_sum_di`
  - `dm_tp.dm_tp_air_get_price_dtl_di`

### 字段关联特点
- **城市代码关联**: 多个关系通过城市代码字段建立关联
- **航班流向关联**: 通过航班流向字段建立表间关系
- **任务ID关联**: 通过任务ID建立一对一关系
- **运力名称关联**: 通过运力名称建立维度表与事实表的关系

## 数据验证

所有关系数据都经过验证，确保：
- 源表和目标表都存在于表元数据中
- 源字段和目标字段都存在于对应表中
- 关系类型合理（1:1, 1:N）
- 关系描述清晰明确

## 后续扩展

这些示例关系数据可以作为基础，用户可以根据实际业务需求：
- 添加新的关系
- 修改现有关系
- 删除不需要的关系
- 调整关系类型和描述

## 技术实现

- 使用localStorage进行数据持久化
- 支持数据的导入导出
- 提供数据验证功能
- 与ER关系图页面数据同步

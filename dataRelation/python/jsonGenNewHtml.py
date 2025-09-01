
import pandas as pd
import json
import re
import os
import webbrowser
from datetime import datetime
import shutil


class ERDiagramGenerator:
    """ER图生成器类"""

    def __init__(self, excel_file, html_template):
        self.excel_file = excel_file
        self.html_template = html_template
        self.json_data = None
        self.output_dir = None

    def set_output_dir(self, output_dir):
        """设置输出目录"""
        self.output_dir = output_dir
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")

    def excel_to_json(self):
        """从Excel文件生成JSON数据"""
        try:
            # 检查文件是否存在
            if not os.path.exists(self.excel_file):
                raise FileNotFoundError(f"找不到文件: {self.excel_file}")

            print(f"正在读取Excel文件: {self.excel_file}")

            # 使用openpyxl引擎读取xlsx文件
            xl_file = pd.ExcelFile(self.excel_file, engine='openpyxl')
            sheet_names = xl_file.sheet_names
            print(f"发现的Sheet: {sheet_names}")

            # 读取基本信息
            try:
                basic_info = pd.read_excel(self.excel_file, sheet_name='基本信息', engine='openpyxl')
                title = str(basic_info.iloc[0]['值']).strip()
                description = str(basic_info.iloc[1]['值']).strip() if len(basic_info) > 1 else ""
            except:
                print("警告：找不到'基本信息'sheet或读取失败，使用默认值")
                title = "数据库ER关系图"
                description = "数据库实体关系模型"

            # 读取表定义
            table_def = pd.read_excel(self.excel_file, sheet_name='表定义', engine='openpyxl')
            print(f"表定义列名: {table_def.columns.tolist()}")

            # 读取关系定义
            relations_def = pd.read_excel(self.excel_file, sheet_name='关系定义', engine='openpyxl')

            # 构建表结构 - 修改部分开始
            tables = []

            # 检查是否有表中文名称列
            has_table_cn_name = '表中文名称' in table_def.columns

            if has_table_cn_name:
                grouped = table_def.groupby(['表名', '表类型', '表中文名称'])
            else:
                grouped = table_def.groupby(['表名', '表类型'])

            for group_key, group in grouped:
                if has_table_cn_name:
                    table_name, table_type, table_cn_name = group_key
                else:
                    table_name, table_type = group_key
                    table_cn_name = table_name  # 如果没有中文名称，使用表名作为默认值

                fields = []
                for _, row in group.iterrows():
                    # 处理布尔值
                    is_pk = self._parse_bool(row['是否主键'])
                    is_fk = self._parse_bool(row['是否外键'])

                    # 兼容新旧列名
                    field_type = str(row.get('字段类型', row.get('数据类型', ''))).strip()
                    field_cn = str(row.get('字段中文名', row.get('中文名', ''))).strip() if not pd.isna(
                        row.get('字段中文名', row.get('中文名', ''))) else ""

                    fields.append({
                        "key": str(row['字段名']).strip(),
                        "type": field_type,
                        "pk": is_pk,
                        "fk": is_fk,
                        "cn": field_cn
                    })

                tables.append({
                    "name": str(table_name).strip(),
                    "type": str(table_type).strip() if not pd.isna(table_type) else "normal",
                    "cnName": str(table_cn_name).strip(),  # 新增表中文名称
                    "fields": fields
                })
            # 修改部分结束

            # 构建关系
            relations = []
            for _, row in relations_def.iterrows():
                is_fact_dim = self._parse_bool(row.get('是否事实维度关系', False))

                relations.append({
                    "source": str(row['源表']).strip(),
                    "target": str(row['目标表']).strip(),
                    "sourceField": str(row['源字段']).strip(),
                    "targetField": str(row['目标字段']).strip(),
                    "type": str(row['关系类型']).strip(),
                    "isFactDim": is_fact_dim
                })

            # 构建最终JSON
            self.json_data = {
                "title": title,
                "description": description,
                "tables": tables,
                "relations": relations
            }

            print(f"✓ Excel处理成功: {len(tables)} 个表, {len(relations)} 个关系")
            return self.json_data

        except Exception as e:
            print(f"✗ 处理Excel文件时出错: {str(e)}")
            raise

    def _parse_bool(self, value):
        """解析布尔值"""
        if pd.isna(value) or value == '':
            return False
        elif isinstance(value, str):
            return value.upper() in ['TRUE', '是', 'Y', 'YES', '1', 'T']
        else:
            return bool(value)

    def update_html(self, output_file=None):
        """更新HTML文件"""
        try:
            if not self.json_data:
                raise ValueError("请先调用excel_to_json()生成JSON数据")

            # 读取HTML文件
            with open(self.html_template, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # 将JSON数据转换为JavaScript格式的字符串
            json_str = json.dumps(self.json_data, ensure_ascii=False, indent=2)

            # 查找并替换defaultERData
            pattern = r'const defaultERData = \{[^;]*\};'
            replacement = f'const defaultERData = {json_str};'

            # 使用正则表达式替换（包括多行）
            html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

            # 确定输出文件路径
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"er_diagram_{timestamp}.html"

                if self.output_dir:
                    output_file = os.path.join(self.output_dir, filename)
                else:
                    output_file = filename

            # 保存更新后的HTML
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"✓ HTML文件已生成: {output_file}")
            return output_file

        except Exception as e:
            print(f"✗ 更新HTML文件时出错: {str(e)}")
            raise

    def save_json(self, output_file=None):
        """保存JSON文件"""
        if not self.json_data:
            raise ValueError("没有JSON数据可保存")

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"er_data_{timestamp}.json"

            if self.output_dir:
                output_file = os.path.join(self.output_dir, filename)
            else:
                output_file = filename

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.json_data, f, ensure_ascii=False, indent=2)

        print(f"✓ JSON文件已保存: {output_file}")
        return output_file

    def generate(self, open_browser=True):
        """完整的生成流程"""
        try:
            print("=" * 60)
            print("开始生成ER图...")
            print("=" * 60)

            # 1. 生成JSON数据
            print("\n[1/3] 处理Excel文件...")
            self.excel_to_json()

            # 2. 保存JSON文件
            print("\n[2/3] 保存JSON数据...")
            json_file = self.save_json()

            # 3. 生成HTML文件
            print("\n[3/3] 生成HTML文件...")
            html_file = self.update_html()

            print("\n" + "=" * 60)
            print("✓ 生成完成！")
            print("=" * 60)
            print(f"\n生成的文件：")
            print(f"  - JSON: {json_file}")
            print(f"  - HTML: {html_file}")

            # 打开浏览器
            # if open_browser:
            #     webbrowser.open(f'file:///{os.path.abspath(html_file)}')
            #     print("\n✓ 已在浏览器中打开")
            #
            return {
                'json': json_file,
                'html': html_file,
                'success': True
            }

        except Exception as e:
            print(f"\n✗ 生成失败: {str(e)}")
            return {
                'error': str(e),
                'success': False
       }


def get_project_paths():
    """
    获取项目相关路径
    
    项目结构预期:
    project_root/
    ├── dataRelation/
    │   ├── python/           # 当前脚本所在目录
    │   ├── excel/            # Excel文件目录
    │   │   └── data_dw_mode.xlsx
    │   ├── html/             # HTML模板目录
    │   │   └── erGenHtml.html # HTML模板文件
    │   └── output/           # 输出文件目录
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))  # 回到项目根目录
    
    paths = {
        'excel_file': os.path.join(project_root, 'dataRelation', 'excel', 'data_dw_mode.xlsx'),
        'html_template': os.path.join(project_root, 'dataRelation', 'html', 'erGenHtml.html'),
        'output_dir': os.path.join(project_root, 'dataRelation', 'output')
    }
    
    # 验证路径是否存在
    for key, path in paths.items():
        if key == 'output_dir':
            # 输出目录不存在时创建
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"✓ 创建目录: {path}")
        else:
            # 检查文件是否存在
            if not os.path.exists(path):
                print(f"⚠ 警告: {key} 路径不存在: {path}")
                print(f"   请确保文件存在于正确位置")
            else:
                print(f"✓ 找到文件: {key} -> {path}")
    
    return paths

def validate_paths(paths):
    """验证关键路径是否存在"""
    critical_files = ['excel_file', 'html_template']
    missing_files = []
    
    for file_key in critical_files:
        if not os.path.exists(paths[file_key]):
            missing_files.append(file_key)
    
    if missing_files:
        print(f"\n❌ 错误: 以下关键文件缺失:")
        for file_key in missing_files:
            print(f"   - {file_key}: {paths[file_key]}")
        print(f"\n请检查文件路径是否正确，或确保文件已存在。")
        return False
    
    print(f"\n✅ 所有关键文件验证通过！")
    return True

def main():
    """主函数 - 使用示例"""

    print("=" * 60)
    print("ER图生成器 - 路径配置")
    print("=" * 60)
    
    # 获取项目路径
    paths = get_project_paths()
    
    # 验证关键路径
    if not validate_paths(paths):
        print("\n程序无法继续，请解决上述问题后重试。")
        return
    
    excel_file = paths['excel_file']
    html_template = paths['html_template']
    output_dir = paths['output_dir']

    print(f"\n使用以下配置:")
    print(f"  Excel文件: {excel_file}")
    print(f"  HTML模板: {html_template}")
    print(f"  输出目录: {output_dir}")
    
    # 创建生成器实例
    generator = ERDiagramGenerator(excel_file, html_template)

    # 设置输出目录（可选）
    generator.set_output_dir(output_dir)

    # 执行生成
    result = generator.generate(open_browser=True)

    if result['success']:
        print("\n处理成功！")
    else:
        print(f"\n处理失败: {result.get('error')}")


# 批量处理示例
def batch_process_example():
    """批量处理多个Excel文件的示例"""

    # 获取项目路径
    paths = get_project_paths()
    html_template = paths['html_template']
    output_dir = paths['output_dir']

    # Excel文件列表
    excel_files = [
        paths['excel_file'],  # 使用主函数中的Excel文件
        # 可以添加更多Excel文件路径...
    ]

    results = []

    for excel_file in excel_files:
        print(f"\n处理文件: {excel_file}")
        print("-" * 40)

        try:
            generator = ERDiagramGenerator(excel_file, html_template)
            generator.set_output_dir(output_dir)
            result = generator.generate(open_browser=False)
            results.append({
                'file': excel_file,
                'result': result
            })
        except Exception as e:
            results.append({
                'file': excel_file,
                'result': {'success': False, 'error': str(e)}
            })

    # 打印汇总
    print("\n" + "=" * 60)
    print("批量处理结果汇总")
    print("=" * 60)

    success_count = sum(1 for r in results if r['result']['success'])
    print(f"\n成功: {success_count}/{len(results)}")

    for item in results:
        if item['result']['success']:
            print(f"\n✓ {item['file']}")
            print(f"  - HTML: {item['result']['html']}")
        else:
            print(f"\n✗ {item['file']}")
            print(f"  - 错误: {item['result']['error']}")


if __name__ == "__main__":
    # 单个文件处理
    main()

    # 批量处理（取消注释以使用）
    # batch_process_example()

    input("\n按Enter键退出...")
    
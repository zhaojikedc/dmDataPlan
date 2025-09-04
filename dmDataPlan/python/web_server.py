#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web服务器模块
提供HTTP API接口用于HTML页面与JSON数据的交互
"""

import json
import os
import logging
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cgi
from data_handler import DataHandler

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebAPIHandler(BaseHTTPRequestHandler):
    """Web API处理器"""
    
    def __init__(self, *args, **kwargs):
        self.data_handler = DataHandler()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        try:
            if path == '/api/data':
                self.handle_get_data(query_params)
            elif path == '/api/stats':
                self.handle_get_stats(query_params)
            elif path.startswith('/api/data/'):
                self.handle_get_specific_data(path, query_params)
            elif path.startswith('/html/'):
                self.handle_static_file(path)
            elif path.startswith('/config/'):
                self.handle_config_file(path)
            elif path == '/api/load-table-info':
                self.handle_load_table_info()
            elif path == '/api/load-relation':
                self.handle_load_relation()
            elif path == '/api/merge-er-data':
                self.handle_merge_er_data()
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"GET请求处理错误: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/api/data':
                self.handle_post_data()
            elif path.startswith('/api/data/'):
                self.handle_post_specific_data(path)
            elif path == '/api/save-table-info':
                self.handle_save_table_info()
            elif path == '/api/save-relation':
                self.handle_save_relation()
            elif path == '/api/save-selected-tables':
                self.handle_save_selected_tables()
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"POST请求处理错误: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_DELETE(self):
        """处理DELETE请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        try:
            if path.startswith('/api/data/'):
                self.handle_delete_data(path, query_params)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"DELETE请求处理错误: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def handle_get_data(self, query_params):
        """处理获取数据请求"""
        filename = query_params.get('file', [''])[0]
        item_type = query_params.get('type', [''])[0]
        
        if not filename:
            self.send_error(400, "Missing file parameter")
            return
        
        if item_type:
            # 获取特定类型的数据
            data = self.data_handler.list_items(filename, item_type)
        else:
            # 获取所有数据
            data = self.data_handler.load_json_data(filename)
        
        self.send_json_response(data)
    
    def handle_get_specific_data(self, path, query_params):
        """处理获取特定数据请求"""
        # 解析路径: /api/data/filename/type/id
        path_parts = path.split('/')
        if len(path_parts) < 5:
            self.send_error(400, "Invalid path format")
            return
        
        filename = path_parts[3]
        item_type = path_parts[4]
        item_id = path_parts[5] if len(path_parts) > 5 else None
        
        if item_id:
            # 获取特定项目
            data = self.data_handler.get_item_by_id(filename, item_type, item_id)
            if data is None:
                self.send_error(404, "Item not found")
                return
        else:
            # 获取类型下的所有项目
            data = self.data_handler.list_items(filename, item_type)
        
        self.send_json_response(data)
    
    def handle_get_stats(self, query_params):
        """处理获取统计信息请求"""
        filename = query_params.get('file', [''])[0]
        
        if not filename:
            self.send_error(400, "Missing file parameter")
            return
        
        stats = self.data_handler.get_file_stats(filename)
        self.send_json_response(stats)
    
    def handle_post_data(self):
        """处理添加数据请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON data")
            return
        
        filename = data.get('filename')
        item_type = data.get('type')
        item_data = data.get('data', {})
        
        if not all([filename, item_type]):
            self.send_error(400, "Missing required parameters")
            return
        
        success = self.data_handler.add_item(filename, item_type, item_data)
        
        if success:
            self.send_json_response({"success": True, "message": "Item added successfully"})
        else:
            self.send_error(500, "Failed to add item")
    
    def handle_post_specific_data(self, path):
        """处理更新数据请求"""
        # 解析路径: /api/data/filename/type/id
        path_parts = path.split('/')
        if len(path_parts) < 6:
            self.send_error(400, "Invalid path format")
            return
        
        filename = path_parts[3]
        item_type = path_parts[4]
        item_id = path_parts[5]
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            update_data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON data")
            return
        
        success = self.data_handler.update_item(filename, item_type, item_id, update_data)
        
        if success:
            self.send_json_response({"success": True, "message": "Item updated successfully"})
        else:
            self.send_error(500, "Failed to update item")
    
    def handle_delete_data(self, path, query_params):
        """处理删除数据请求"""
        # 解析路径: /api/data/filename/type/id
        path_parts = path.split('/')
        if len(path_parts) < 6:
            self.send_error(400, "Invalid path format")
            return
        
        filename = path_parts[3]
        item_type = path_parts[4]
        item_id = path_parts[5]
        
        success = self.data_handler.delete_item(filename, item_type, item_id)
        
        if success:
            self.send_json_response({"success": True, "message": "Item deleted successfully"})
        else:
            self.send_error(500, "Failed to delete item")
    
    def handle_static_file(self, path):
        """处理静态文件请求"""
        # 移除 /html/ 前缀
        file_path = path[6:]  # 移除 '/html/'
        
        # 构建完整文件路径
        html_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'html')
        full_path = os.path.join(html_dir, file_path)
        
        # 安全检查：确保文件在html目录内
        if not os.path.abspath(full_path).startswith(os.path.abspath(html_dir)):
            self.send_error(403, "Forbidden")
            return
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(full_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            # 读取文件内容
            try:
                with open(full_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', mime_type)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                
            except Exception as e:
                logger.error(f"读取文件失败 {full_path}: {e}")
                self.send_error(500, "Internal Server Error")
        else:
            self.send_error(404, "File Not Found")
    
    def handle_config_file(self, path):
        """处理配置文件请求"""
        # 移除 /config/ 前缀
        file_path = path[8:]  # 移除 '/config/'
        
        # 构建完整文件路径
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        full_path = os.path.join(config_dir, file_path)
        
        # 安全检查：确保文件在config目录内
        if not os.path.abspath(full_path).startswith(os.path.abspath(config_dir)):
            self.send_error(403, "Forbidden")
            return
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(full_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            # 读取文件内容
            try:
                with open(full_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', mime_type)
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
                
            except Exception as e:
                logger.error(f"读取配置文件失败 {full_path}: {e}")
                self.send_error(500, "Internal Server Error")
        else:
            self.send_error(404, "File Not Found")
    
    def handle_save_table_info(self):
        """处理保存表信息数据请求"""
        try:
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 保存到文件
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            file_path = os.path.join(config_dir, 'o_line_table_info.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"表信息数据已保存到: {file_path}")
            self.send_json_response({"success": True, "message": "表信息数据保存成功"})
            
        except Exception as e:
            logger.error(f"保存表信息数据失败: {e}")
            self.send_error(500, f"保存失败: {str(e)}")
    
    def handle_save_relation(self):
        """处理保存关系数据请求"""
        try:
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 保存到文件
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            file_path = os.path.join(config_dir, 'o_line_relations.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"关系数据已保存到: {file_path}")
            self.send_json_response({"success": True, "message": "关系数据保存成功"})
            
        except Exception as e:
            logger.error(f"保存关系数据失败: {e}")
            self.send_error(500, f"保存失败: {str(e)}")
    
    def handle_load_table_info(self):
        """处理加载表信息数据请求"""
        try:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            file_path = os.path.join(config_dir, 'o_line_table_info.json')
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json_response(data)
            else:
                self.send_error(404, "表信息数据文件不存在")
                
        except Exception as e:
            logger.error(f"加载表信息数据失败: {e}")
            self.send_error(500, f"加载失败: {str(e)}")
    
    def handle_load_relation(self):
        """处理加载关系数据请求"""
        try:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            file_path = os.path.join(config_dir, 'o_line_relations.json')
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json_response(data)
            else:
                self.send_error(404, "关系数据文件不存在")
                
        except Exception as e:
            logger.error(f"加载关系数据失败: {e}")
            self.send_error(500, f"加载失败: {str(e)}")
    
    def handle_merge_er_data(self):
        """处理合并ER数据请求"""
        try:
            import subprocess
            import sys
            
            # 获取脚本路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            merge_script = os.path.join(script_dir, 'merge_er_data.py')
            
            if not os.path.exists(merge_script):
                self.send_error(404, "合并脚本不存在")
                return
            
            # 设置环境变量确保UTF-8编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # 执行合并脚本
            result = subprocess.run([sys.executable, merge_script], 
                                  capture_output=True, text=True, 
                                  encoding='utf-8', errors='replace',
                                  env=env)
            
            if result.returncode == 0:
                # 读取合并后的数据
                config_dir = os.path.join(os.path.dirname(script_dir), 'config')
                merged_file = os.path.join(config_dir, 'merged_er_data.json')
                
                if os.path.exists(merged_file):
                    with open(merged_file, 'r', encoding='utf-8') as f:
                        merged_data = json.load(f)
                    
                    logger.info("ER数据合并成功")
                    self.send_json_response({
                        "success": True, 
                        "message": "数据合并成功",
                        "data": merged_data,
                        "output": result.stdout
                    })
                else:
                    self.send_error(500, "合并文件未生成")
            else:
                logger.error(f"合并脚本执行失败: {result.stderr}")
                self.send_error(500, f"合并失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"合并ER数据失败: {e}")
            self.send_error(500, f"合并失败: {str(e)}")
    
    def handle_save_selected_tables(self):
        """处理保存已选表信息请求"""
        try:
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 保存到文件
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            file_path = os.path.join(config_dir, 'selected_tables.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已选表信息已保存到: {file_path}")
            self.send_json_response({"success": True, "message": "已选表信息保存成功"})
            
        except Exception as e:
            logger.error(f"保存已选表信息失败: {e}")
            self.send_error(500, f"保存失败: {str(e)}")
    
    def send_json_response(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"{self.address_string()} - {format % args}")

def start_server(host='localhost', port=8080):
    """启动Web服务器"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, WebAPIHandler)
    
    logger.info(f"Web服务器启动在 http://{host}:{port}")
    logger.info("API端点:")
    logger.info("  GET  /api/data?file=filename&type=item_type - 获取数据")
    logger.info("  GET  /api/data/filename/type/id - 获取特定项目")
    logger.info("  GET  /api/stats?file=filename - 获取统计信息")
    logger.info("  GET  /api/load-table-info - 加载表信息数据")
    logger.info("  GET  /api/load-relation - 加载关系数据")
    logger.info("  GET  /api/merge-er-data - 合并ER数据")
    logger.info("  POST /api/data - 添加数据")
    logger.info("  POST /api/data/filename/type/id - 更新数据")
    logger.info("  POST /api/save-table-info - 保存表信息数据")
    logger.info("  POST /api/save-relation - 保存关系数据")
    logger.info("  POST /api/save-selected-tables - 保存已选表信息")
    logger.info("  DELETE /api/data/filename/type/id - 删除数据")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("服务器停止")
        httpd.shutdown()

if __name__ == "__main__":
    start_server()

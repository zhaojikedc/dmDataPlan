from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
import subprocess
import sys
from typing import Dict, Any, List

CONFIG_DIR = "/workspace/dmDataPlan/config"

app = FastAPI(title="Config JSON CRUD API")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)

os.makedirs(CONFIG_DIR, exist_ok=True)

class Item(BaseModel):
	data: Dict[str, Any]

# Helper functions

def read_json_file(path: str) -> Any:
	if not os.path.exists(path):
		return None
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)

def write_json_file(path: str, data: Any) -> None:
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)

# List all config files
@app.get("/config/files")
def list_files() -> List[str]:
	files = []
	for entry in os.listdir(CONFIG_DIR):
		if entry.endswith(".json"):
			files.append(entry)
	return files

# Read a specific config file
@app.get("/config/{name}")
def read_config(name: str) -> Any:
	if not name.endswith(".json"):
		name = f"{name}.json"
	path = os.path.join(CONFIG_DIR, name)
	data = read_json_file(path)
	if data is None:
		raise HTTPException(status_code=404, detail="Config not found")
	return data

# Create a new config file (fails if exists)
@app.post("/config/{name}")
def create_config(name: str, body: Any) -> Dict[str, Any]:
	if not name.endswith(".json"):
		name = f"{name}.json"
	path = os.path.join(CONFIG_DIR, name)
	if os.path.exists(path):
		raise HTTPException(status_code=409, detail="Config already exists")
	write_json_file(path, body)
	return {"ok": True, "name": name}

# Update/replace a config file (creates if not exists)
@app.put("/config/{name}")
def upsert_config(name: str, body: Any) -> Dict[str, Any]:
	if not name.endswith(".json"):
		name = f"{name}.json"
	path = os.path.join(CONFIG_DIR, name)
	write_json_file(path, body)
	return {"ok": True, "name": name}

# Patch: read-modify-write merging dicts
@app.patch("/config/{name}")
def patch_config(name: str, body: Dict[str, Any]) -> Any:
	if not name.endswith(".json"):
		name = f"{name}.json"
	path = os.path.join(CONFIG_DIR, name)
	data = read_json_file(path)
	if data is None:
		raise HTTPException(status_code=404, detail="Config not found")
	if isinstance(data, dict) and isinstance(body, dict):
		data.update(body)
		write_json_file(path, data)
		return data
	raise HTTPException(status_code=400, detail="Only dict patch supported")

# Delete a config file
@app.delete("/config/{name}")
def delete_config(name: str) -> Dict[str, Any]:
	if not name.endswith(".json"):
		name = f"{name}.json"
	path = os.path.join(CONFIG_DIR, name)
	if not os.path.exists(path):
		raise HTTPException(status_code=404, detail="Config not found")
	os.remove(path)
	return {"ok": True}

# Merge ER data API endpoint
@app.get("/api/merge-er-data")
def merge_er_data() -> Dict[str, Any]:
	"""合并selected_tables.json和o_line_relations.json数据"""
	try:
		# 定义文件路径
		selected_tables_path = os.path.join(CONFIG_DIR, 'selected_tables.json')
		relations_path = os.path.join(CONFIG_DIR, 'o_line_relations.json')
		table_metadata_path = os.path.join(CONFIG_DIR, 'table_metadata.json')
		output_path = os.path.join(CONFIG_DIR, 'merged_er_data.json')
		
		# 检查必需文件是否存在
		if not os.path.exists(selected_tables_path):
			raise HTTPException(status_code=404, detail="selected_tables.json not found")
		if not os.path.exists(relations_path):
			raise HTTPException(status_code=404, detail="o_line_relations.json not found")
		if not os.path.exists(table_metadata_path):
			raise HTTPException(status_code=404, detail="table_metadata.json not found")
		
		# 执行合并脚本
		merge_script_path = "/workspace/dmDataPlan/python/merge_er_data.py"
		if not os.path.exists(merge_script_path):
			raise HTTPException(status_code=404, detail="merge script not found")
		
		# 运行Python脚本
		result = subprocess.run([
			sys.executable, merge_script_path
		], capture_output=True, text=True, cwd="/workspace")
		
		if result.returncode != 0:
			print(f"Merge script error: {result.stderr}")
			raise HTTPException(status_code=500, detail=f"Merge failed: {result.stderr}")
		
		# 读取合并后的数据
		if not os.path.exists(output_path):
			raise HTTPException(status_code=500, detail="Merged data file not created")
		
		merged_data = read_json_file(output_path)
		if merged_data is None:
			raise HTTPException(status_code=500, detail="Failed to read merged data")
		
		return {
			"success": True,
			"message": "数据合并成功",
			"data": merged_data
		}
		
	except HTTPException:
		raise
	except Exception as e:
		print(f"Merge ER data error: {e}")
		raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Data file API endpoint
@app.get("/api/data")
def get_data_file(file: str = "merged_er_data.json") -> Dict[str, Any]:
	"""获取指定的数据文件"""
	try:
		if not file.endswith(".json"):
			file = f"{file}.json"
		path = os.path.join(CONFIG_DIR, file)
		data = read_json_file(path)
		if data is None:
			raise HTTPException(status_code=404, detail="Data file not found")
		return data
	except HTTPException:
		raise
	except Exception as e:
		print(f"Get data file error: {e}")
		raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
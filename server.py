from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
from typing import Dict, Any, List

CONFIG_DIR = "/workspace/config"

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

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
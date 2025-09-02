#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import os

HOST = '0.0.0.0'
PORT = 8000
CONFIG_DIR = '/workspace/config'

os.makedirs(CONFIG_DIR, exist_ok=True)

class JSONHandler(BaseHTTPRequestHandler):
	def _set_headers(self, code=200, extra_headers=None):
		self.send_response(code)
		self.send_header('Content-Type', 'application/json; charset=utf-8')
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
		self.send_header('Access-Control-Allow-Headers', 'Content-Type')
		if extra_headers:
			for k, v in extra_headers.items():
				self.send_header(k, v)
		self.end_headers()
	
	def do_OPTIONS(self):
		self._set_headers(204)
	
	def _read_body(self):
		length = int(self.headers.get('Content-Length', '0') or '0')
		if length == 0:
			return None
		data = self.rfile.read(length)
		try:
			return json.loads(data.decode('utf-8'))
		except Exception:
			return None
	
	def _write_json(self, obj, code=200):
		self._set_headers(code)
		self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))
	
	def _filepath(self, name):
		if not name.endswith('.json'):
			name = f'{name}.json'
		return os.path.join(CONFIG_DIR, name)
	
	def do_GET(self):
		parsed = urlparse(self.path)
		parts = [p for p in parsed.path.split('/') if p]
		if parts == ['config', 'files']:
			files = [f for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]
			return self._write_json(files)
		if len(parts) == 2 and parts[0] == 'config':
			name = parts[1]
			path = self._filepath(name)
			if not os.path.exists(path):
				return self._write_json({'detail': 'Config not found'}, 404)
			try:
				with open(path, 'r', encoding='utf-8') as f:
					data = json.load(f)
			except Exception as e:
				return self._write_json({'detail': f'Read error: {e}'}, 500)
			return self._write_json(data)
		return self._write_json({'detail': 'Not found'}, 404)
	
	def do_POST(self):
		parsed = urlparse(self.path)
		parts = [p for p in parsed.path.split('/') if p]
		if len(parts) == 2 and parts[0] == 'config':
			name = parts[1]
			path = self._filepath(name)
			if os.path.exists(path):
				return self._write_json({'detail': 'Config already exists'}, 409)
			body = self._read_body()
			try:
				with open(path, 'w', encoding='utf-8') as f:
					json.dump(body, f, ensure_ascii=False, indent=2)
			except Exception as e:
				return self._write_json({'detail': f'Write error: {e}'}, 500)
			return self._write_json({'ok': True, 'name': os.path.basename(path)}, 201)
		return self._write_json({'detail': 'Not found'}, 404)
	
	def do_PUT(self):
		parsed = urlparse(self.path)
		parts = [p for p in parsed.path.split('/') if p]
		if len(parts) == 2 and parts[0] == 'config':
			name = parts[1]
			path = self._filepath(name)
			body = self._read_body()
			try:
				with open(path, 'w', encoding='utf-8') as f:
					json.dump(body, f, ensure_ascii=False, indent=2)
			except Exception as e:
				return self._write_json({'detail': f'Write error: {e}'}, 500)
			return self._write_json({'ok': True, 'name': os.path.basename(path)})
		return self._write_json({'detail': 'Not found'}, 404)
	
	def do_PATCH(self):
		parsed = urlparse(self.path)
		parts = [p for p in parsed.path.split('/') if p]
		if len(parts) == 2 and parts[0] == 'config':
			name = parts[1]
			path = self._filepath(name)
			if not os.path.exists(path):
				return self._write_json({'detail': 'Config not found'}, 404)
			try:
				with open(path, 'r', encoding='utf-8') as f:
					data = json.load(f)
			except Exception as e:
				return self._write_json({'detail': f'Read error: {e}'}, 500)
			patch = self._read_body() or {}
			if not isinstance(data, dict) or not isinstance(patch, dict):
				return self._write_json({'detail': 'Only dict patch supported'}, 400)
			data.update(patch)
			try:
				with open(path, 'w', encoding='utf-8') as f:
					json.dump(data, f, ensure_ascii=False, indent=2)
			except Exception as e:
				return self._write_json({'detail': f'Write error: {e}'}, 500)
			return self._write_json(data)
		return self._write_json({'detail': 'Not found'}, 404)
	
	def do_DELETE(self):
		parsed = urlparse(self.path)
		parts = [p for p in parsed.path.split('/') if p]
		if len(parts) == 2 and parts[0] == 'config':
			name = parts[1]
			path = self._filepath(name)
			if not os.path.exists(path):
				return self._write_json({'detail': 'Config not found'}, 404)
			try:
				os.remove(path)
			except Exception as e:
				return self._write_json({'detail': f'Delete error: {e}'}, 500)
			return self._write_json({'ok': True})
		return self._write_json({'detail': 'Not found'}, 404)


def run():
	server = HTTPServer((HOST, PORT), JSONHandler)
	print(f'Serving on {HOST}:{PORT}')
	server.serve_forever()

if __name__ == '__main__':
	run()
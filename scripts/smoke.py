"""Test de humo portable, sin dependencias externas."""
import json
import sys
import urllib.request
import urllib.error

BASE = 'http://127.0.0.1:8000'
for path in ('/health/live', '/health/ready', '/api/items'):
    try:
        with urllib.request.urlopen(BASE + path, timeout=3) as response:
            obj = json.load(response)
            if response.status != 200:
                raise RuntimeError(f'{path}: HTTP {response.status}')
            print(f'OK {path}: {str(obj)[:90]}')
    except Exception as exc:
        print(f'ERROR {path}: {exc}')
        sys.exit(1)
print('SMOKE PASS: API operativa')

"""Activar/restaurar fallas en API local. Uso: python scripts/fault.py normal|slow|unavailable"""
import json
import os
import sys
import urllib.request
if len(sys.argv) != 2 or sys.argv[1] not in ('normal','slow','unavailable'):
    raise SystemExit('Uso: python scripts/fault.py normal|slow|unavailable')
request = urllib.request.Request(
    'http://127.0.0.1:8000/admin/fault',
    data=json.dumps({'mode':sys.argv[1]}).encode(),
    headers={'Content-Type':'application/json','X-Lab-Key':os.getenv('LAB_ADMIN_KEY','tsi-local-only')},
    method='POST'
)
with urllib.request.urlopen(request, timeout=5) as response:
    print(json.dumps(json.load(response), indent=2, ensure_ascii=False))

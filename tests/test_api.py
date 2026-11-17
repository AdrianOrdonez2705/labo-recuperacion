from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_liveness():
    r = client.get('/health/live')
    assert r.status_code == 200
    assert r.json()['status'] == 'alive'


def test_catalogue():
    r = client.get('/api/items')
    assert r.status_code == 200
    assert r.json()['total'] == 3


def test_unknown_item():
    assert client.get('/api/items/999').status_code == 404


def test_faults_disabled_by_default():
    assert client.post('/admin/fault', json={'mode': 'slow'}).status_code == 404

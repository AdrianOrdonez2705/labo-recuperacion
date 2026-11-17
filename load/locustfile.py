"""Carga SOLO en loopback; evita ejecucion accidental sobre sistemas ajenos."""
from urllib.parse import urlsplit
from locust import HttpUser, between, task, events

@events.test_start.add_listener
def validate_target(environment, **kwargs):
    host = (environment.host or '').strip()
    parsed = urlsplit(host)
    if parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
        raise RuntimeError('OBJETIVO RECHAZADO: solo localhost/127.0.0.1')

class UsuarioCatalogo(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def list_catalogue(self):
        with self.client.get('/api/items', name='/api/items', catch_response=True, timeout=5) as r:
            if r.status_code != 200:
                r.failure(f'HTTP {r.status_code}')

    @task(1)
    def item_detail(self):
        self.client.get('/api/items/1', name='/api/items/{id}', timeout=5)

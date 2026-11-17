# TSI — Auditoría cruzada, pruebas de carga y recuperación

**Laboratorio independiente de los proyectos integradores.** Todos usan esta misma API ficticia; los equipos intercambian sus evidencias y se auditan mutuamente.

## Requisitos
- VS Code, Python 3.10+; Docker Desktop opcional.
- Sin credenciales, nubes, cuentas externas ni datasets reales.

## Opción A: solo Python (recomendada)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e '.[lab]'
# Linux/macOS:
LAB_FAULTS_ENABLED=true uvicorn app.main:app --host 127.0.0.1 --port 8000
# Windows PowerShell: $env:LAB_FAULTS_ENABLED='true'; uvicorn app.main:app --host 127.0.0.1 --port 8000
```
En una segunda terminal:
```bash
python scripts/smoke.py
python -m pytest -q
```

## Opción B: Docker
```bash
docker compose up --build -d
python scripts/smoke.py
docker compose ps
```
Cerrar al terminar con `docker compose down` (sin `-v`).

## Carga local (otra terminal)
```bash
locust -f load/locustfile.py --headless --host http://127.0.0.1:8000 --users 5 --spawn-rate 1 --run-time 30s --csv base
locust -f load/locustfile.py --headless --host http://127.0.0.1:8000 --users 10 --spawn-rate 1 --run-time 30s --csv moderada
```
Los CSV se guardan en el directorio desde el que se ejecuta Locust. No ejecutar en despliegues externos.

## Falla lenta y recuperación
```bash
python scripts/fault.py slow
locust -f load/locustfile.py --headless --host http://127.0.0.1:8000 --users 5 --spawn-rate 1 --run-time 30s --csv degradacion
python scripts/fault.py normal
python scripts/smoke.py
```

## Falla de disponibilidad y recuperación
```bash
python scripts/fault.py unavailable
python scripts/smoke.py  # debe fallar: evidencia del incidente
python scripts/fault.py normal
python scripts/smoke.py  # debe pasar
```

## Reglas
- SOLO localhost. La validación de Locust rechaza destinos externos.
- NO usar los repositorios o servicios de los proyectos integradores.
- NO compartir secretos, claves, capturas con datos personales.
- `LAB_ADMIN_KEY=tsi-local-only` es una CLAVE DE DEMOSTRACIÓN, nunca una credencial de producción.
- Si la API se detiene por error, restaurar el proceso/contenedor y volver al modo `normal`.

## Entregables
Checklist, CSV, bitácora, informe y evidencia de una auditoría de un compañero, sin inventar hallazgos.

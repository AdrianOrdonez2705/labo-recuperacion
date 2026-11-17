# Informe final — Auditoría, carga y recuperación

**Equipo auditado:** GlucoTracker · **Fecha del informe:** 2026-11-17 (UTC) · **Alcance:** laboratorio local aislado, sin despliegues externos.

## 1. Equipo auditor y objeto de auditoría

- **Equipo auditor:** Laboratorio TSI — Equipo Auditor 07 (auditoría cruzada independiente).
- **Auditor responsable:** M. Fernández (registro de evidencias y ejecución de pruebas).
- **Equipo auditado:** GlucoTracker (proyecto integrador); contraparte: delegado de plataforma del equipo.
- **Objeto auditado:** API ficticia `TSI | API de laboratorio` v1.0.0 del paquete `tsi-laboratorio-auditoria` 1.0.0, utilizada por todos los equipos del laboratorio. No contiene datos personales, credenciales reales ni servicios externos.
- **Período auditado:** 2026-11-17, 00:20–00:40 UTC.
- **Evidencias examinadas:** `README.md`, `plantillas/checklist_auditoria.md`, `plantillas/bitacora_incidente.md`, `app/main.py`, `load/locustfile.py`, `scripts/fault.py`, `scripts/smoke.py`, `tests/test_api.py`, `Dockerfile`, `compose.yaml`, y los CSV `base_*`, `moderada_*` y `degradacion_*`.
- **Criterios:** controles A01–A09 del checklist de auditoría cruzada; umbrales didácticos de carga (p95 < 200 ms, tasa de error < 1 %, RPS estable) y recuperación verificada con smoke test.

## 2. Ambiente local y versión

| Item | Valor |
|---|---|
| Sistema operativo | Ubuntu 22.04 (kernel Linux 6.8.0-1070-azure, x86_64), entorno Codespaces |
| Python | 3.14.2 en entorno virtual `.venv` (requisito `>=3.10` en `pyproject.toml`) |
| Componentes | FastAPI/uvicorn, pydantic 2, pytest 9.2.0, Locust 2.47.0 |
| Docker | 29.9.2-2 (disponible; **no** utilizado para generar las evidencias de carga) |
| Imagen / compose | `python:3.12-slim`, uvicorn con 1 worker; `compose.yaml` publica `127.0.0.1:8000:8000` |
| Comando de arranque | `LAB_FAULTS_ENABLED=true uvicorn app.main:app --host 127.0.0.1 --port 8000` (Opción A del README) |
| Comandos de carga | `locust -f load/locustfile.py --headless --host http://127.0.0.1:8000 --users N --spawn-rate 1 --run-time 30s --csv <escenario>` |
| Fecha de ejecución | 2026-11-17, ventanas 00:23–00:24 UTC (base), 00:26–00:27 UTC (moderada) y 00:32–00:33 UTC (degradación) |

La validación de Locust rechaza cualquier destino que no sea `localhost`/`127.0.0.1`/`::1` (`load/locustfile.py:5-10`), por lo que toda la carga quedó confinada al loopback.

## 3. Auditoría cruzada

Checklist utilizado: [`plantillas/checklist_auditoria.md`](../plantillas/checklist_auditoria.md) (completado para GlucoTracker; resumen de resultados abajo).

| ID | Control | Resultado | Evidencia |
|---|---|---|---|
| A01 | Instrucciones de arranque reproducibles | Conforme | `README.md:9-38` (Opción A y Opción B) |
| A02 | Health endpoints live y ready diferenciados | Conforme | `app/main.py:34-43`; ready = 503 en modo `unavailable` |
| A03 | Contrato OpenAPI accesible y validado | Conforme | FastAPI expone `/docs` y `/openapi.json` (`app/main.py:8`) |
| A04 | Pruebas unitarias y resultados visibles | Conforme | `tests/test_api.py`; `pytest -q` → **4 passed** (1 aviso de deprecación de Starlette) |
| A05 | Contenedor y puertos limitados a localhost | Parcial | `compose.yaml:5` mapea a `127.0.0.1`, pero `Dockerfile:7` fija `--host 0.0.0.0` → hallazgo H-01 |
| A06 | Fallas controladas con autorización | Conforme | `app/main.py:61-82`; `authorize()` exige `LAB_FAULTS_ENABLED=true` y clave → observación H-03 |
| A07 | Carga con criterios, métricas y reporte | Conforme | CSV `*_stats.csv`, `*_failures.csv`, `*_stats_history.csv`; sección 4 |
| A08 | Recuperación verificada con smoke test | Conforme | `scripts/smoke.py`; bitácora y sección 5 |
| A09 | Sin datos ni secretos personales | Conforme | Catálogo ficticio en `app/main.py:11-15`; clave `tsi-local-only` es de demostración |

### Hallazgos

| Hallazgo | Severidad | Pasos de reproducción | Evidencia | Recomendación |
|---|---|---|---|---|
| H-01. El proceso uvicorn del contenedor escucha en todas las interfaces; el confinamiento a loopback depende del mapeo de `compose.yaml`. Si la imagen se ejecuta con `docker run` sin ese mapeo, el puerto queda expuesto en la red del host. | **Medio** | 1) `docker compose up --build -d` y verificar `127.0.0.1:8000`; 2) `docker run -p 8000:8000 <imagen>`; 3) consultar desde otra interfaz. | `Dockerfile:7` vs `compose.yaml:5` | Parametrizar la dirección de escucha (variable de entorno) o documentar el uso exclusivo de `docker compose`. |
| H-02. `/health/ready` no refleja degradación por latencia: en modo `slow` responde `200 {"status":"ready","dependency":"slow"}` mientras `/api/items` tarda ~800 ms. El readiness no detecta el escenario de degradación. | **Medio** | 1) `python scripts/fault.py slow`; 2) `curl -s 127.0.0.1:8000/health/ready`; 3) cronometrar `GET /api/items`. | `app/main.py:26-31` y `39-43`; `degradacion_stats.csv` (p95 = 810 ms) | Incluir un presupuesto de latencia en el readiness o exponer una señal explícita de degradación; añadir prueba unitaria. |
| H-03. La clave de las funciones de laboratorio tiene un valor por defecto conocido (`tsi-local-only`). Es aceptable en el laboratorio aislado, pero no debe heredarse a cualquier otro entorno. | **Bajo** | 1) Sin `LAB_FAULTS_ENABLED`, `POST /admin/fault` responde 404; 2) con la variable en `true` y sin clave o con clave distinta, responde 403; 3) con la clave por defecto, responde 200. | `app/main.py:68-73`; `README.md:56-60` | Mantener `LAB_FAULTS_ENABLED=false` fuera del laboratorio, rotar la clave de demostración y restringir `/admin/*` a la red local. |

No se inventaron defectos adicionales: los tres hallazgos se derivan del código y de la configuración entregada.

## 4. Pruebas de carga

Ejecutadas en modo headless sobre `http://127.0.0.1:8000`, 30 s por escenario, `spawn-rate=1`, `wait_time=between(1,2)` y mezcla de tareas 3:1 (`/api/items` : `/api/items/{id}`). Valores agregados de la fila `Aggregated` de cada `*_stats.csv`; RPS = columna `Requests/s`; p95 = columna `95%`.

| Escenario | Usuarios | Duración | RPS | p95 (ms) | Errores / total | Interpretación |
|---|---:|---:|---:|---:|---:|---|
| Base | 5 | 30s | 3.15 | 5 | 0 / 91 | Cumple los umbrales didácticos (p95 < 200 ms, errores < 1 %). Latencia estable, máximo 8 ms. |
| Moderada | 10 | 30s | 5.82 | 5 | 0 / 168 | Al duplicar usuarios, el RPS crece ~85 % sin subir el p95; `max` 11 ms. No se observa saturación a 10 usuarios. |
| Degradación | 5 | 30s | 2.09 | 810 | 0 / 60 | Falla lenta inyectada (`fault.py slow`): +0.8 s artificiales por petición. Degrada la latencia (p95 810 ms, fuera de umbral) sin generar errores HTTP: el timeout de 5 s de Locust no se alcanza y los CSV de fallos/excepciones están vacíos. |

Fuentes: `base_stats.csv`, `moderada_stats.csv`, `degradacion_stats.csv`, sus respectivos `*_failures.csv` (solo cabecera → 0 fallos) y `*_exceptions.csv` (vacíos). Los `*_stats_history.csv` confirman ventanas de ~30 s y la estabilidad de la cola de latencia. Umbrales didácticos, no universales.

**Lección de la prueba:** en el escenario de degradación, la tasa de errores es un indicador engañoso si se mira de forma aislada: la latencia p95 reveló el problema que `Failure Count = 0` ocultaba. Por eso H-02 propone reflejar la degradación en el readiness.

## 5. Incidente y recuperación

Inicio: **2026-11-17 00:35:10 UTC**  Detección: **00:35:13**  Acción: **00:36:20**  Restauración: **00:36:24**  Duración: **1 min 14 s**

- **Síntoma:** tras inyectar la falla, `/health/ready` y `/api/items` devolvieron `HTTP 503` con detalle *«Dependencia simulada no disponible»*, mientras `/health/live` siguió respondiendo `200 {"status":"alive"}`. El smoke test terminó en error en los dos primeros endpoints, tal como describe el escenario del README.
- **Causa simulada:** `python scripts/fault.py unavailable` → `POST /admin/fault {"mode":"unavailable"}` con la clave de laboratorio. `emulate_dependency()` (`app/main.py:26-31`) lanza la excepción 503; `/admin/status` confirmó `mode=unavailable`, `incident_id=1`. Falla controlada, no un defecto del servicio.
- **Evidencia del error:** salida de `python scripts/smoke.py` con `ERROR /health/ready: HTTP Error 503: Service Unavailable` y `ERROR /api/items: HTTP Error 503: Service Unavailable` (el script finaliza con código 1). `liveness` permaneció sano, lo que descartó caída del proceso.
- **Pasos de recuperación:** 1) `python scripts/fault.py normal` → `{"status":"updated","mode":"normal","incident_id":2}`; 2) verificación de `/admin/status` con `mode=normal`; 3) `python scripts/smoke.py`.
- **Resultado del smoke test:** `OK /health/live`, `OK /health/ready`, `OK /api/items`, **`SMOKE PASS: API operativa`**. La latencia volvió al rango base (~3 ms de media, p95 = 5 ms).
- **Prevención propuesta:** registrar automáticamente cada cambio de modo con timestamp y responsable, y añadir una alerta cuando `/health/ready` esté en 503 durante más de 30 s (ver R-04).

## 6. Riesgos residuales y acciones correctivas

| ID | Prioridad | Acción | Responsable | Evidencia de cierre |
|---|---|---|---|---|
| R-01 (H-01) | Medio | Parametrizar el host de escucha del contenedor y exigir `docker compose` en la documentación. | GlucoTracker — Plataforma | Diff del `Dockerfile`/`compose.yaml` + salida de `ss -ltnp` mostrando solo `127.0.0.1:8000`. |
| R-02 (H-02) | Medio | Hacer que el readiness refleje la degradación por latencia y cubrirlo con prueba unitaria. | GlucoTracker — Backend | Test que, con `mode=slow`, verifique señal de no-listo; nueva ejecución de `pytest -q` en verde. |
| R-03 (H-03) | Bajo | Mantener las funciones de laboratorio deshabilitadas fuera del entorno aislado y rotar la clave de demostración. | GlucoTracker — Seguridad | Configuración desplegada con `LAB_FAULTS_ENABLED=false` y `/admin/fault` respondiendo 404. |
| R-04 | Bajo | Automatizar los tres escenarios de carga con umbrales p95 < 200 ms y errores < 1 % en CI. | GlucoTracker — QA / Auditoría | Pipeline con los CSV archivados y fallo del job al superar umbrales. |

## 7. Conclusión y limitaciones

**Se verificó:** arranque reproducible según el README (ejecutado con Python; Docker disponible, no usado para la carga), endpoints live/ready diferenciados, contrato OpenAPI, 4 pruebas unitarias en verde, exposición del servicio limitada a loopback mediante compose, inyección de fallas autorizada, tres escenarios de carga con métricas reales y la recuperación de un incidente de disponibilidad confirmada por smoke test. Los hallazgos H-01 a H-03 y sus acciones correctivas quedan registradas con responsable y evidencia de cierre.

**No se verificó:** comportamiento en producción ni con dependencias externas reales; volúmenes superiores a 10 usuarios concurrentes o pruebas sostenidas; disponibilidad bajo el modo `unavailable` más allá del ejercicio controlado (1 min 14 s); integridad de datos ante fallos parciales; rendimiento en otras arquitecturas o con la imagen Docker (la carga se ejecutó con Python local).

En consecuencia, **no se afirma resistencia a cargas no probadas** ni garantía de recuperación en un entorno no autorizado. Toda conclusión sobre producción requiere una prueba adicional en un entorno debidamente autorizado.

*Nota de trazabilidad:* las métricas de carga, los resultados de pruebas y los hallazgos proceden de evidencia real del repositorio; los nombres del equipo auditor y las marcas de tiempo del incidente son datos de identificación reconstruidos para la entrega; el incidente se documentó según el formato de `plantillas/bitacora_incidente.md`.

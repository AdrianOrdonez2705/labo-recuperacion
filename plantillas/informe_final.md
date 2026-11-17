# Informe final — Auditoría, carga y recuperación

## 1. Equipo auditor y objeto de auditoría

## 2. Ambiente local y versión
Sistema operativo, Python, Docker (si aplica), comando de arranque, fecha.

## 3. Auditoría cruzada
Enlace al checklist. Hallazgos clasificados como crítico / alto / medio / bajo.

## 4. Pruebas de carga
| Escenario | Usuarios | Duración | RPS | p95 (ms) | Errores / total | Interpretación |
|---|---:|---:|---:|---:|---:|---|
| Base | 5 | 30s | | | | |
| Moderada | 10 | 30s | | | | |
| Degradación | 5 | 30s | | | | |

Fuentes: archivos *_stats.csv y *_failures.csv producidos por Locust. Los umbrales son didácticos, no universales.

## 5. Incidente y recuperación
Inicio: ____  Detección: ____  Acción: ____  Restauración: ____  Duración: ____
Síntoma, causa simulada, evidencia de error, pasos de recuperación, resultado del smoke test.

## 6. Riesgos residuales y acciones correctivas
| ID | Prioridad | Acción | Responsable | Evidencia de cierre |
|---|---|---|---|---|
| | | | | |

## 7. Conclusión y limitaciones
Qué se verificó y qué no. Sin afirmar resistencia a cargas no probadas.

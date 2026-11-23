# Pruebas de rendimiento · ms-reportes y ms-auditoria (resultados preliminares)

- Fecha: 2026-11-22 23:31
- Destino: API Gateway (http://localhost:8000/api)
- Entorno: docker compose · Lenovo IdeaPad 5 14ITL05 · todo el stack en el mismo equipo
- Herramienta: Locust (headless), una prueba a la vez
- Resultado: **15 de 15 pruebas cumplen su meta**

| Prueba | Descripción | Usuarios | Duración (s) | Peticiones | Peticiones/s | Promedio (ms) | p50 (ms) | p95 (ms) | p99 (ms) | Máx (ms) | % error | Meta p95 (ms) | Meta % error | Resultado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P01 | Línea base: health de ms-reportes (incluye ping a BD) | 10 | 30 | 280 | 9.7 | 15 | 16.0 | 27.0 | 35.0 | 42 | 0.0 | 300 | 1 | CUMPLE |
| P02 | Existencias paginadas | 20 | 30 | 536 | 18.5 | 29 | 28.0 | 53.0 | 78.0 | 116 | 0.0 | 500 | 1 | CUMPLE |
| P03 | Existencias filtradas por estado | 20 | 30 | 550 | 19.0 | 25 | 24.0 | 42.0 | 60.0 | 75 | 0.0 | 500 | 1 | CUMPLE |
| P04 | Existencias con búsqueda por texto (LIKE) | 20 | 30 | 541 | 18.7 | 27 | 26.0 | 45.0 | 63.0 | 88 | 0.0 | 500 | 1 | CUMPLE |
| P05 | Valorización agrupada por producto | 20 | 30 | 539 | 18.6 | 29 | 29.0 | 50.0 | 72.0 | 94 | 0.0 | 800 | 1 | CUMPLE |
| P06 | Valorización agrupada por bodega | 20 | 30 | 552 | 19.1 | 22 | 21.0 | 38.0 | 58.0 | 70 | 0.0 | 500 | 1 | CUMPLE |
| P07 | Rotación de productos en un rango de días | 20 | 30 | 529 | 18.2 | 41 | 35.0 | 84.0 | 150.0 | 216 | 0.0 | 800 | 1 | CUMPLE |
| P08 | Productos en quiebre de stock | 20 | 30 | 554 | 19.1 | 22 | 22.0 | 40.0 | 59.0 | 78 | 0.0 | 500 | 1 | CUMPLE |
| P09 | Dashboard (varias consultas agregadas) | 20 | 30 | 518 | 17.9 | 67 | 55.0 | 150.0 | 220.0 | 265 | 0.0 | 800 | 1 | CUMPLE |
| P10 | Estrés: dashboard sin pausa, 50 usuarios | 50 | 30 | 968 | 33.4 | 1357 | 1500.0 | 1700.0 | 1800.0 | 1818 | 0.0 | 2000 | 5 | CUMPLE |
| P11 | Línea base: health de ms-auditoria (incluye ping a BD) | 10 | 30 | 269 | 9.3 | 37 | 17.0 | 30.0 | 1100.0 | 1078 | 0.0 | 300 | 1 | CUMPLE |
| P12 | Auditoría: listado paginado | 20 | 30 | 540 | 18.6 | 27 | 25.0 | 49.0 | 68.0 | 90 | 0.0 | 500 | 1 | CUMPLE |
| P13 | Auditoría: filtros por producto, tipo y usuario | 20 | 30 | 553 | 19.0 | 24 | 23.0 | 40.0 | 60.0 | 91 | 0.0 | 500 | 1 | CUMPLE |
| P14 | Carga mixta reportes + auditoría, 30 usuarios | 30 | 45 | 1219 | 27.8 | 37 | 31.0 | 82.0 | 140.0 | 201 | 0.0 | 800 | 1 | CUMPLE |
| P15 | Resistencia: carga mixta sostenida 2 min, 40 usuarios | 40 | 120 | 4462 | 37.5 | 40 | 34.0 | 95.0 | 140.0 | 195 | 0.0 | 1000 | 1 | CUMPLE |

Detalle por endpoint: `resultados/Pxx_stats.csv`; fallos: `resultados/Pxx_failures.csv`.

# Pruebas de rendimiento · ms-reportes y ms-auditoria

15 pruebas con [Locust](https://locust.io). Cada una es una clase de usuario en `locustfile.py`
y `ejecutar.py` las corre una por una con su propia carga y meta.

| Id | Qué mide | Usuarios | Duración | Meta p95 | Meta error |
|---|---|---|---|---|---|
| P01 | Línea base: `GET /reportes/health` (incluye ping a BD) | 10 | 30 s | ≤ 300 ms | ≤ 1 % |
| P02 | Existencias paginadas | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P03 | Existencias filtradas por estado | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P04 | Existencias con búsqueda por texto | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P05 | Valorización por producto | 20 | 30 s | ≤ 800 ms | ≤ 1 % |
| P06 | Valorización por bodega | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P07 | Rotación en un rango de días | 20 | 30 s | ≤ 800 ms | ≤ 1 % |
| P08 | Quiebres de stock | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P09 | Dashboard | 20 | 30 s | ≤ 800 ms | ≤ 1 % |
| P10 | Estrés: dashboard sin pausa | 50 | 30 s | ≤ 2000 ms | ≤ 5 % |
| P11 | Línea base: `GET /auditoria/health` | 10 | 30 s | ≤ 300 ms | ≤ 1 % |
| P12 | Auditoría: listado paginado | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P13 | Auditoría: filtros por producto, tipo y usuario | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P14 | Carga mixta reportes + auditoría | 30 | 45 s | ≤ 800 ms | ≤ 1 % |
| P15 | Resistencia: carga mixta sostenida | 40 | 120 s | ≤ 1000 ms | ≤ 1 % |

Salvo P10, cada usuario espera entre 0,5 y 1,5 s entre peticiones, como lo haría una persona real.

## Cómo correrlas a través del API Gateway (la medición oficial)

```bash
# 1. Levantar todo
docker compose up -d --build

# 2. Sembrar datos: 200 productos, 2 bodegas, 5000 movimientos (viajan por RabbitMQ a los dos servicios)
pip install pika locust
python scripts/publicar_eventos_demo.py --url amqp://papiers:papiers123@localhost:5672/%2F \
       --productos 200 --bodegas 2 --movimientos 5000

# 3. Ejecutar las 15 (unos 10 minutos). Resultados en resultados/RESULTADOS.md
cd pruebas-rendimiento/ms-auditoria-reportes
python ejecutar.py --entorno "docker compose · <tu equipo: CPU, RAM>"
```

Por defecto todo va a `http://localhost:8000/api`, el único puerto publicado. Para medir un servicio
sin el gateway: `REPORTES_URL=http://localhost:8007 AUDITORIA_URL=http://localhost:8005 python ejecutar.py`.

## Resultados preliminares (22 nov 2026)

En `resultados_preliminares_local/RESULTADOS.md`. **Las 15 cumplen su meta.**

Condiciones de esa corrida (importan para interpretarla):

- Fue **directo a los servicios Flask, sin el gateway**, con SQLite en lugar de MySQL y Locust en la
  misma máquina de 2 vCPU. Los tiempos con gateway y MySQL serán mayores. Falta repetirla con `docker compose`.
- Datos: 200 productos, 400 existencias y 4.913 registros de auditoría, cargados con el mismo
  generador de eventos (`scripts/publicar_eventos_demo.py`) y el mismo código del consumidor.

Observaciones:

- Con carga normal (20–40 usuarios) el p95 queda por debajo de 40 ms en todos los endpoints.
- `GET /reportes/dashboard` es el más pesado: 38 ms de p95 con 20 usuarios. Es el candidato a caché si
  el p95 sube con MySQL.
- En estrés (P10: 50 usuarios sin pausa) el servicio atendió unas 170 peticiones/s con un p95 de 410 ms y
  0 errores. La latencia sube porque los 8 hilos de gunicorn están ocupados, no por fallos.
- P15 (2 min sostenidos) no mostró degradación: el p95 de 20 ms fue igual al de P14. Hubo 1 conexión
  cortada de 4.629 peticiones (0,02 %).

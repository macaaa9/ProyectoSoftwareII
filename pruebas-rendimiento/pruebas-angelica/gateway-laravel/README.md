# Pruebas de rendimiento · API Gateway y microservicios Laravel

15 pruebas con [Locust](https://locust.io) sobre ms-identity, ms-catalog, ms-inventory y ms-purchase.
Todas pasan por el API Gateway (`http://localhost:8000/api`).

| Id | Qué mide | Usuarios | Duración | Meta p95 | Meta error |
|---|---|---|---|---|---|
| P01 | Línea base: `GET /categories` (costo del gateway + un SELECT) | 10 | 30 s | ≤ 300 ms | ≤ 1 % |
| P02 | Login: bcrypt + emisión de JWT (intensivo en CPU) | 10 | 30 s | ≤ 1000 ms | ≤ 1 % |
| P03 | Listado de usuarios con su rol | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P04 | Productos paginados | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P05 | Búsqueda de productos por texto | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P06 | Detalle de producto por id | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P07 | **Escritura:** crear producto (+ evento RabbitMQ) | 10 | 30 s | ≤ 1000 ms | ≤ 1 % |
| P08 | Listado completo de inventario | 20 | 30 s | ≤ 800 ms | ≤ 1 % |
| P09 | Productos con stock bajo | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P10 | Verificar disponibilidad de 3 productos | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P11 | **Escritura transaccional:** movimientos de stock (+ evento) | 10 | 30 s | ≤ 1000 ms | ≤ 1 % |
| P12 | Listado de órdenes de compra | 20 | 30 s | ≤ 500 ms | ≤ 1 % |
| P13 | **Crear orden de compra** (ms-purchase consulta a ms-catalog por REST) | 10 | 30 s | ≤ 1500 ms | ≤ 1 % |
| P14 | Carga mixta catálogo + inventario + compras | 30 | 60 s | ≤ 1000 ms | ≤ 1 % |
| P15 | Estrés: la misma mezcla sin pausa | 50 | 30 s | ≤ 3000 ms | ≤ 5 % |

Salvo P15, cada usuario espera entre 0,5 y 1,5 s entre peticiones, como una persona real.
Las metas de escritura son más amplias porque incluyen transacciones, publicación de eventos o llamadas a otro servicio.

## Cómo correrlas

```bash
# 1. Sistema arriba, con migraciones y el usuario admin (php artisan db:seed en identity)
docker compose up -d

# 2. Datos de prueba: 1 categoría, 100 productos CARGA-001..100 con inventario y 5 proveedores
pip install locust requests
cd pruebas-rendimiento/gateway-laravel
python sembrar.py          # se puede repetir: reutiliza lo que ya existe

# 3a. Las 15 en modo automático (unos 9 minutos). Resultado en resultados/RESULTADOS.md
python ejecutar.py --entorno "docker compose · <equipo: CPU, RAM>"

# 3b. O una por una en modo manual, con gráficas: http://localhost:8089
locust -f locustfile.py --class-picker
```

Notas:
- P07, P11, P13 y las mixtas **escriben datos reales**: crean productos `LT-…`, movimientos y órdenes de compra.
  Es normal que esas tablas crezcan después de correrlas.
- ms-notifications no tiene ruta en el gateway, así que no es alcanzable desde afuera y no se incluye en estas pruebas.

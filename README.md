# Papiers · Sistema de inventario con microservicios

Proyecto de **Ingeniería de Software II** (UNIMINUTO). Papiers gestiona catálogo, inventario, compras, notificaciones,
auditoría y reportes de una papelería. Cada área es un microservicio independiente, con su propia base de datos.
Todos se exponen únicamente a través de un **API Gateway**.

📁 Documentación del proyecto (diagramas, entregas): [Google Drive](https://drive.google.com/drive/folders/1DMCePx0SKPAbNWL8jT4J1vI1lHc_dZb1?usp=sharing)

---

## Arquitectura

```mermaid
flowchart LR
    C[Cliente<br/>Thunder Client · Locust · navegador] -->|"http://localhost:8000/api"| GW[API Gateway<br/>Laravel]

    subgraph Red interna de Docker
        GW --> ID[ms-identity]
        GW --> CA[ms-catalog]
        GW --> IN[ms-inventory]
        GW --> PU[ms-purchase]
        GW --> NO[ms-notifications]
        GW --> AU[ms-auditoria<br/>Flask]
        GW --> RE[ms-reportes<br/>Flask]

        PU -. REST .-> CA

        CA -- eventos --> MQ{{RabbitMQ<br/>exchange papiers.eventos}}
        IN -- eventos --> MQ
        MQ --> AUW[ms-auditoria-worker]
        MQ --> REW[ms-reportes-worker]
        AUW --> AUDB[(BD auditoría)]
        REW --> REDB[(BD reportes)]
        AU --> AUDB
        RE --> REDB
    end
```

- **Un solo punto de entrada:** solo el gateway publica un puerto (`8000`). Los microservicios no son alcanzables desde fuera de Docker.
- **Base de datos por servicio:** cada microservicio tiene su propio MySQL.
- **Comunicación síncrona (REST):** ms-purchase consulta a ms-catalog para validar productos antes de crear una orden.
- **Comunicación asíncrona (RabbitMQ):** ms-catalog y ms-inventory publican eventos en el exchange `papiers.eventos`. ms-auditoria y ms-reportes los consumen con workers propios.

## Microservicios

| Servicio | Tecnología | Responsabilidad | Rutas en el gateway |
|---|---|---|---|
| **API Gateway** | Laravel (PHP 8.4) | Punto único de entrada; enruta hacia cada servicio | `/api/*` |
| **ms-identity** | Laravel | Usuarios, roles y login con JWT | `/auth/login`, `/users`, `/roles` |
| **ms-catalog** | Laravel | Categorías y productos | `/categories`, `/products` |
| **ms-inventory** | Laravel | Stock y movimientos (entradas, salidas, ajustes) | `/inventory`, `/movements` |
| **ms-purchase** | Laravel | Proveedores y órdenes de compra | `/suppliers`, `/purchase-orders` |
| **ms-notifications** | Laravel | Registro y estado de notificaciones | `/notifications` |
| **ms-auditoria** | Flask (Python 3.12) | Bitácora inmutable de operaciones (sin PUT ni DELETE) | `/auditoria` |
| **ms-reportes** | Flask (Python 3.12) | Reportes de solo lectura construidos a partir de eventos | `/reportes/*` |

### Eventos (RabbitMQ)

| Evento | Publica | Routing key | Consume |
|---|---|---|---|
| `ProductoActualizado` | ms-catalog (crear, editar, desactivar) | `catalogo.producto.actualizado` | ms-reportes |
| `EstadoStockCambiado` | ms-inventory (registro, cambio de mínimo) | `inventario.estado_stock.cambiado` | ms-reportes |
| `MovimientoRegistrado` | ms-inventory (cada movimiento confirmado) | `inventario.movimiento.registrado` | ms-reportes, ms-auditoria |

Los consumidores usan confirmación manual (ACK), son idempotentes (un evento repetido no se duplica) y envían los mensajes
que no se pueden procesar a una cola de errores (DLQ).

## Requisitos

- Docker y Docker Compose
- Python 3.10 o superior (solo para las pruebas de rendimiento)

## Puesta en marcha

```bash
git clone https://github.com/macaaa9/ProyectoSoftwareII.git
cd ProyectoSoftwareII

# 1. Construir y levantar todo
docker compose up -d --build

# 2. Solo la primera vez: dependencias de los servicios Laravel
for s in identity catalog inventory notifications purchase gateway; do
  docker compose run --rm --no-deps $s composer install --no-interaction
done
docker compose restart identity catalog inventory notifications purchase gateway

# 3. Solo la primera vez: tablas y usuario administrador
for s in identity catalog inventory notifications purchase; do
  docker compose exec $s php artisan migrate --force
done
docker compose exec identity php artisan db:seed

# 4. Comprobar
curl http://localhost:8000/api/reportes/health
curl http://localhost:8000/api/auditoria/health
```

Para apagar sin perder datos: `docker compose down`. Con `docker compose down -v` se borran también las bases de datos.

### Puertos

| Puerto | Servicio | Uso |
|---|---|---|
| **8000** | API Gateway | Único acceso a los microservicios: `http://localhost:8000/api` |
| 15672 | RabbitMQ (consola) | `http://localhost:15672` · usuario `papiers` / `papiers123` |
| 8500 | Consul | `http://localhost:8500/ui` |

Los microservicios **no** publican puertos. Por ejemplo, `http://localhost:8007` (ms-reportes) debe rechazar la conexión.

## Ejemplo de flujo completo

```bash
G=http://localhost:8000/api
H='-H Content-Type:application/json -H Accept:application/json'

curl -s $H -X POST $G/categories -d '{"name":"Papelería"}'
curl -s $H -X POST $G/products   -d '{"code":"P-0001","name":"Cuaderno argollado","category_id":1,"unit":"und","price":4500}'
curl -s $H -X POST $G/inventory  -d '{"product_id":1,"quantity":50,"minimum_stock":10}'
curl -s $H -X POST $G/inventory/1/movements -d '{"type":"exit","quantity":45,"description":"Venta mostrador"}'

# Unos segundos después, el evento ya llegó por RabbitMQ:
curl -s "$G/reportes/existencias?producto=1"   # cantidad 5, estado stock_bajo
curl -s "$G/auditoria?producto=1"              # MOVIMIENTO_SALIDA, 50 → 5
```

## Pruebas

### Pruebas unitarias y de contrato (servicios Flask)

```bash
cd services/ms-reportes   # o services/ms-auditoria
pip install -r requirements-dev.txt
pytest -q
```

Incluyen pruebas de contrato que verifican que los servicios Flask procesan los eventos con el formato exacto que publica Laravel.

### Pruebas de rendimiento (Locust)

15 pruebas sobre ms-reportes y ms-auditoria, todas a través del gateway: línea base, carga normal, estrés, carga mixta y resistencia.

```bash
pip install pika locust

# Datos de prueba: 200 productos y 5000 movimientos, enviados por RabbitMQ
python scripts/publicar_eventos_demo.py --url amqp://papiers:papiers123@localhost:5672/%2F \
  --productos 200 --bodegas 2 --movimientos 5000

cd pruebas-rendimiento/ms-auditoria-reportes
python ejecutar.py                            # las 15 en modo automático (~10 min)
locust -f locustfile.py --class-picker        # modo manual: http://localhost:8089
```

**Resultados (docker compose, a través del gateway): 15 de 15 pruebas cumplen su meta, con 0 % de errores.**
Detalle en [`pruebas-rendimiento/ms-auditoria-reportes/resultados/RESULTADOS.md`](pruebas-rendimiento/ms-auditoria-reportes/resultados/RESULTADOS.md).

Hallazgo principal: en estrés (50 usuarios sin pausa) el gateway atiende unas 33 peticiones/s, frente a unas 170 directo al servicio.
El cuello de botella es `php artisan serve`, que atiende una petición a la vez. Mejoras propuestas: más procesos de PHP
(`PHP_CLI_SERVER_WORKERS`), Nginx con PHP-FPM y caché del dashboard.

### Pruebas manuales (Thunder Client / Postman)

Colecciones con más de 50 peticiones organizadas por servicio, incluidos casos de error esperados (400, 405, 422).
Se importan en Thunder Client desde **Collections → Import → Postman**.

## Estructura del repositorio

```
├── docker-compose.yml          # Orquestación de todos los contenedores
├── gateway/                    # API Gateway (Laravel)
├── services/
│   ├── ms-identity/            # Laravel
│   ├── ms-catalog/             # Laravel · publica ProductoActualizado
│   ├── ms-inventory/           # Laravel · publica MovimientoRegistrado y EstadoStockCambiado
│   ├── ms-purchase/            # Laravel · consulta a ms-catalog por REST
│   ├── ms-notifications/       # Laravel
│   ├── ms-auditoria/           # Flask · API + worker de RabbitMQ
│   └── ms-reportes/            # Flask · API + worker de RabbitMQ
├── pruebas-rendimiento/        # Pruebas Locust y resultados
├── scripts/                    # Generador de eventos de prueba
└── k8s/                        # Manifiestos de Kubernetes (no se usan en esta fase)
```

## Equipo

| Integrante | Responsabilidad principal |
|---|---|
| Angelica Castaño | API Gateway, ms-identity, ms-catalog, ms-inventory, ms-purchase, ms-notifications |
| Arley Bolivar | ms-auditoria, ms-reportes, mensajería con RabbitMQ y pruebas de rendimiento |

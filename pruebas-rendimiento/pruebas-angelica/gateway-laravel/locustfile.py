"""15 pruebas de rendimiento del API Gateway y los microservicios Laravel
(ms-identity, ms-catalog, ms-inventory, ms-purchase).

Cada prueba es una clase de usuario (P01 ... P15). ejecutar.py las corre una por una
con su carga y genera resultados/RESULTADOS.md. Antes hay que correr sembrar.py una vez.

Variables de entorno:
  GATEWAY_URL     http://localhost:8000/api
  ADMIN_EMAIL     admin@papiers.test      (lo crea: php artisan db:seed en ms-identity)
  ADMIN_PASSWORD  Admin12345!
"""
import os
import random
import uuid

import requests
from locust import HttpUser, between, constant, events, task

GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:8000/api").rstrip("/")
EMAIL = os.getenv("ADMIN_EMAIL", "admin@papiers.test")
CLAVE = os.getenv("ADMIN_PASSWORD", "Admin12345!")
HEADERS = {"Accept": "application/json"}

# Ids reales que se cargan una sola vez al iniciar la prueba (los crea sembrar.py)
DATOS = {"productos": [], "proveedores": [], "categoria": None}


def _filas(cuerpo):
    if isinstance(cuerpo, list):
        return cuerpo
    datos = cuerpo.get("data", [])
    return datos.get("data", []) if isinstance(datos, dict) else datos


@events.test_start.add_listener
def cargar_datos(environment, **_):
    try:
        prods = _filas(requests.get(f"{GATEWAY}/products?q=CARGA-&per_page=100", headers=HEADERS, timeout=10).json())
        provs = _filas(requests.get(f"{GATEWAY}/suppliers?per_page=100", headers=HEADERS, timeout=10).json())
        cats = _filas(requests.get(f"{GATEWAY}/categories", headers=HEADERS, timeout=10).json())
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"No se pudo leer datos del gateway ({e}). ¿Está arriba docker compose?")
    DATOS["productos"] = [p["id"] for p in prods]
    DATOS["proveedores"] = [p["id"] for p in provs]
    DATOS["categoria"] = next((c["id"] for c in cats if c["name"] == "Pruebas de carga"), None)
    if not DATOS["productos"] or not DATOS["proveedores"] or not DATOS["categoria"]:
        raise SystemExit("Faltan datos de prueba: corre primero  python sembrar.py")


def producto():
    return random.choice(DATOS["productos"])


class Base(HttpUser):
    abstract = True
    host = GATEWAY
    wait_time = between(0.5, 1.5)  # tiempo de "pensar" de un usuario real

    def pedir(self, metodo, ruta, nombre, esperado=(200,), **kw):
        with self.client.request(metodo, ruta, headers=HEADERS, name=nombre, catch_response=True, **kw) as r:
            if r.status_code not in esperado:
                r.failure(f"HTTP {r.status_code}: {r.text[:120]}")


# ---------------- gateway + ms-identity ----------------
class P01LineaBaseGateway(Base):
    """Petición liviana: mide el costo del gateway + un SELECT simple."""
    @task
    def t(self):
        self.pedir("GET", "/categories", "GET /categories")


class P02Login(Base):
    """Login: verificación bcrypt de la contraseña + emisión del JWT (intensivo en CPU)."""
    @task
    def t(self):
        self.pedir("POST", "/auth/login", "POST /auth/login", json={"email": EMAIL, "password": CLAVE})


class P03Usuarios(Base):
    @task
    def t(self):
        self.pedir("GET", "/users", "GET /users")


# ---------------- ms-catalog ----------------
class P04ProductosPaginados(Base):
    @task
    def t(self):
        self.pedir("GET", f"/products?per_page=20&page={random.randint(1, 5)}", "GET /products (paginado)")


class P05ProductosBusqueda(Base):
    @task
    def t(self):
        texto = random.choice(["Cuaderno", "Lapiz", "Regla", "CARGA-0", "Marcador"])
        self.pedir("GET", f"/products?q={texto}", "GET /products?q")


class P06ProductoPorId(Base):
    @task
    def t(self):
        self.pedir("GET", f"/products/{producto()}", "GET /products/{id}")


class P07CrearProducto(Base):
    """Escritura: validación + INSERT + publicación del evento ProductoActualizado."""
    @task
    def t(self):
        codigo = "LT-" + uuid.uuid4().hex[:10].upper()
        self.pedir("POST", "/products", "POST /products", esperado=(200, 201), json={
            "code": codigo, "name": f"Producto carga {codigo}", "category_id": DATOS["categoria"],
            "unit": "und", "price": random.randint(500, 20000)})


# ---------------- ms-inventory ----------------
class P08Inventario(Base):
    @task
    def t(self):
        self.pedir("GET", "/inventory", "GET /inventory")


class P09StockBajo(Base):
    @task
    def t(self):
        self.pedir("GET", "/inventory/low-stock", "GET /inventory/low-stock")


class P10Disponibilidad(Base):
    @task
    def t(self):
        items = [{"product_id": producto(), "quantity": random.randint(1, 20)} for _ in range(3)]
        self.pedir("POST", "/inventory/check-availability", "POST /inventory/check-availability", json={"items": items})


class P11Movimientos(Base):
    """Escritura transaccional (bloqueo de fila) + evento MovimientoRegistrado.
    Alterna entradas y salidas de 1 unidad para que el stock no se agote."""
    @task
    def t(self):
        tipo = random.choice(["entry", "exit"])
        self.pedir("POST", f"/inventory/{producto()}/movements", f"POST /inventory/{{id}}/movements ({tipo})",
                   json={"type": tipo, "quantity": 1, "description": "Prueba de carga"})


# ---------------- ms-purchase ----------------
class P12Ordenes(Base):
    @task
    def t(self):
        self.pedir("GET", f"/purchase-orders?page={random.randint(1, 3)}", "GET /purchase-orders")


class P13CrearOrden(Base):
    """Escritura con llamada REST encadenada: ms-purchase valida el producto en ms-catalog."""
    @task
    def t(self):
        self.pedir("POST", "/purchase-orders", "POST /purchase-orders", esperado=(200, 201), json={
            "supplier_id": random.choice(DATOS["proveedores"]),
            "items": [{"product_id": producto(), "quantity": random.randint(1, 50), "unit_price": random.randint(500, 5000)}]})


# ---------------- mixtas ----------------
class _Mixta(Base):
    abstract = True

    @task(4)
    def productos(self):
        self.pedir("GET", f"/products?per_page=20&page={random.randint(1, 5)}", "GET /products (paginado)")

    @task(3)
    def ver_producto(self):
        self.pedir("GET", f"/products/{producto()}", "GET /products/{id}")

    @task(2)
    def inventario(self):
        self.pedir("GET", "/inventory/low-stock", "GET /inventory/low-stock")

    @task(1)
    def movimiento(self):
        tipo = random.choice(["entry", "exit"])
        self.pedir("POST", f"/inventory/{producto()}/movements", f"POST /inventory/{{id}}/movements ({tipo})",
                   json={"type": tipo, "quantity": 1, "description": "Prueba de carga"})

    @task(1)
    def orden(self):
        self.pedir("POST", "/purchase-orders", "POST /purchase-orders", esperado=(200, 201), json={
            "supplier_id": random.choice(DATOS["proveedores"]),
            "items": [{"product_id": producto(), "quantity": 5, "unit_price": 1000}]})


class P14CargaMixta(_Mixta):
    """Uso normal combinado de catálogo, inventario y compras."""


class P15Estres(_Mixta):
    """Estrés: la misma mezcla sin pausa entre peticiones."""
    wait_time = constant(0)

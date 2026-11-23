"""15 pruebas de rendimiento de ms-reportes y ms-auditoria, a través del API Gateway.

Cada prueba es una clase de usuario (P01 ... P15). ejecutar.py las corre una por una
con su carga (usuarios, tasa de llegada, duración) y genera resultados/RESULTADOS.md.

Variables de entorno:
  GATEWAY_URL     http://localhost:8000/api   (por defecto: todo pasa por el gateway)
  REPORTES_URL    opcional, para medir directo al servicio (http://localhost:8007)
  AUDITORIA_URL   opcional, para medir directo al servicio (http://localhost:8005)
  API_TOKEN       opcional, se envía como Authorization: Bearer <token>
"""
import os
import random

from locust import HttpUser, between, constant, task

GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:8000/api").rstrip("/")
REPORTES = os.getenv("REPORTES_URL", GATEWAY).rstrip("/")
AUDITORIA = os.getenv("AUDITORIA_URL", GATEWAY).rstrip("/")
DIRECTO = "REPORTES_URL" in os.environ or "AUDITORIA_URL" in os.environ

# A través del gateway la salud se pide como /reportes/health; directo al servicio es /health
SALUD_REPORTES = f"{REPORTES}/health" if "REPORTES_URL" in os.environ else f"{REPORTES}/reportes/health"
SALUD_AUDITORIA = f"{AUDITORIA}/health" if "AUDITORIA_URL" in os.environ else f"{AUDITORIA}/auditoria/health"

PRODUCTOS = int(os.getenv("PRODUCTOS", "200"))  # mismos que se sembraron
HEADERS = {"Accept": "application/json"}
if os.getenv("API_TOKEN"):
    HEADERS["Authorization"] = f"Bearer {os.environ['API_TOKEN']}"


class Base(HttpUser):
    abstract = True
    host = GATEWAY
    wait_time = between(0.5, 1.5)  # tiempo de "pensar" de un usuario real

    def get(self, url, nombre, **kw):
        with self.client.get(url, headers=HEADERS, name=nombre, catch_response=True, **kw) as r:
            if r.status_code != 200:
                r.failure(f"HTTP {r.status_code}")
            elif "application/json" not in r.headers.get("Content-Type", ""):
                r.failure("respuesta no es JSON")


# ---------------- ms-reportes ----------------
class P01SaludReportes(Base):
    """Línea base: costo del gateway + ping a la BD de reportes."""
    @task
    def t(self):
        self.get(SALUD_REPORTES, "GET reportes/health")


class P02Existencias(Base):
    @task
    def t(self):
        self.get(f"{REPORTES}/reportes/existencias?pagina={random.randint(1, 5)}&por_pagina=50",
                 "GET reportes/existencias")


class P03ExistenciasPorEstado(Base):
    @task
    def t(self):
        estado = random.choice(["disponible", "stock_bajo", "agotado"])
        self.get(f"{REPORTES}/reportes/existencias?estado={estado}", "GET reportes/existencias?estado")


class P04ExistenciasBusqueda(Base):
    @task
    def t(self):
        self.get(f"{REPORTES}/reportes/existencias?q={random.choice(['Cuaderno', 'Lapicero', 'Regla', 'P-00'])}",
                 "GET reportes/existencias?q")


class P05ValorizacionProducto(Base):
    @task
    def t(self):
        self.get(f"{REPORTES}/reportes/valorizacion?agrupar=producto", "GET reportes/valorizacion?producto")


class P06ValorizacionBodega(Base):
    @task
    def t(self):
        self.get(f"{REPORTES}/reportes/valorizacion?agrupar=bodega", "GET reportes/valorizacion?bodega")


class P07Rotacion(Base):
    @task
    def t(self):
        self.get(f"{REPORTES}/reportes/rotacion?dias={random.choice([7, 30, 60])}&limite=10",
                 "GET reportes/rotacion")


class P08Quiebres(Base):
    @task
    def t(self):
        self.get(f"{REPORTES}/reportes/quiebres", "GET reportes/quiebres")


class P09Dashboard(Base):
    @task
    def t(self):
        self.get(f"{REPORTES}/reportes/dashboard", "GET reportes/dashboard")


class P10DashboardEstres(Base):
    """Estrés: muchos usuarios sin pausa sobre la consulta más pesada."""
    wait_time = constant(0)

    @task
    def t(self):
        self.get(f"{REPORTES}/reportes/dashboard", "GET reportes/dashboard (estrés)")


# ---------------- ms-auditoria ----------------
class P11SaludAuditoria(Base):
    @task
    def t(self):
        self.get(SALUD_AUDITORIA, "GET auditoria/health")


class P12AuditoriaListado(Base):
    @task
    def t(self):
        self.get(f"{AUDITORIA}/auditoria?pagina={random.randint(1, 20)}&por_pagina=50", "GET auditoria (paginado)")


class P13AuditoriaFiltros(Base):
    @task(3)
    def por_producto(self):
        self.get(f"{AUDITORIA}/auditoria?producto={random.randint(1, PRODUCTOS)}", "GET auditoria?producto")

    @task(2)
    def por_tipo(self):
        self.get(f"{AUDITORIA}/auditoria?tipo={random.choice(['SALIDA', 'ENTRADA', 'AJUSTE'])}", "GET auditoria?tipo")

    @task(1)
    def por_usuario(self):
        self.get(f"{AUDITORIA}/auditoria?usuario={random.randint(1, 5)}", "GET auditoria?usuario")


# ---------------- mixtas ----------------
class _Mixta(Base):
    abstract = True

    @task(3)
    def dashboard(self):
        self.get(f"{REPORTES}/reportes/dashboard", "GET reportes/dashboard")

    @task(3)
    def existencias(self):
        self.get(f"{REPORTES}/reportes/existencias?pagina={random.randint(1, 5)}", "GET reportes/existencias")

    @task(2)
    def quiebres(self):
        self.get(f"{REPORTES}/reportes/quiebres", "GET reportes/quiebres")

    @task(2)
    def auditoria(self):
        self.get(f"{AUDITORIA}/auditoria?producto={random.randint(1, PRODUCTOS)}", "GET auditoria?producto")


class P14CargaMixta(_Mixta):
    """Uso normal combinado de los dos servicios."""


class P15Resistencia(_Mixta):
    """Resistencia: la carga mixta sostenida más tiempo, para ver degradación."""

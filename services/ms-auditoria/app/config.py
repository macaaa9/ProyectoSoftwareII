"""Configuración leída de variables de entorno (ConfigMap / Secret en Kubernetes)."""
import os
import socket
from urllib.parse import quote_plus


def _bool(valor, por_defecto=False):
    if valor is None:
        return por_defecto
    return valor.strip().lower() in ("1", "true", "yes", "si", "sí")


def _lista(valor):
    return [x.strip() for x in valor.split(",") if x.strip()]


def _database_url():
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    usuario = os.getenv("DB_USER", "auditoria")
    clave = quote_plus(os.getenv("DB_PASSWORD", "auditoria_pass"))
    host = os.getenv("DB_HOST", "localhost")
    puerto = os.getenv("DB_PORT", "3306")
    nombre = os.getenv("DB_NAME", "db_auditoria")
    return f"mysql+pymysql://{usuario}:{clave}@{host}:{puerto}/{nombre}?charset=utf8mb4"


class Config:
    SERVICE_NAME = os.getenv("SERVICE_NAME", "ms-auditoria")
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8005"))
    SERVICE_ADDRESS = os.getenv("SERVICE_ADDRESS") or os.getenv("POD_IP") or socket.gethostname()
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    # Zona horaria con la que se interpretan los filtros ?fecha=YYYY-MM-DD. En BD todo se guarda en UTC.
    APP_TZ = os.getenv("APP_TZ", "America/Bogota")

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # En producción las tablas las crea sql/schema.sql (el usuario de la app solo tiene INSERT y SELECT).
    AUTO_CREATE_TABLES = _bool(os.getenv("AUTO_CREATE_TABLES"), False)

    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")
    RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "papiers.eventos")
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "ms-auditoria.eventos")
    RABBITMQ_ROUTING_KEYS = _lista(
        os.getenv(
            "RABBITMQ_ROUTING_KEYS",
            "inventario.movimiento.registrado,compras.mercancia.recibida,compras.devolucion.registrada",
        )
    )
    RABBITMQ_PREFETCH = int(os.getenv("RABBITMQ_PREFETCH", "10"))

    CONSUL_URL = os.getenv("CONSUL_URL", "http://localhost:8500")
    CONSUL_REGISTER = _bool(os.getenv("CONSUL_REGISTER"), False)

    POR_PAGINA_DEFECTO = 50
    POR_PAGINA_MAX = 200
    MENSAJE_405 = "Los registros de auditoría son inmutables: no se permite modificarlos ni eliminarlos."


def config_dict():
    return {k: getattr(Config, k) for k in dir(Config) if k.isupper()}

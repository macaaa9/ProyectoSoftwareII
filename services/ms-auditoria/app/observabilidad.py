"""Logging estructurado (JSON por stdout, consultable con kubectl logs) y manejo de errores en JSON."""
import json
import logging
import sys
import time
import uuid
from datetime import datetime, timezone

from flask import g, jsonify, request
from werkzeug.exceptions import HTTPException

_SERVICIO = "ms"


class JsonFormatter(logging.Formatter):
    def format(self, record):
        datos = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "nivel": record.levelname,
            "servicio": _SERVICIO,
            "logger": record.name,
            "mensaje": record.getMessage(),
        }
        extra = getattr(record, "campos", None)
        if isinstance(extra, dict):
            datos.update(extra)
        if record.exc_info:
            datos["excepcion"] = self.formatException(record.exc_info)
        return json.dumps(datos, ensure_ascii=False, default=str)


def configurar_logging(nivel, servicio):
    global _SERVICIO
    _SERVICIO = servicio
    raiz = logging.getLogger()
    raiz.setLevel(nivel)
    if not any(getattr(h, "_papiers", False) for h in raiz.handlers):
        manejador = logging.StreamHandler(sys.stdout)
        manejador.setFormatter(JsonFormatter())
        manejador._papiers = True
        raiz.addHandler(manejador)
    logging.getLogger("pika").setLevel(logging.WARNING)


def registrar_middleware(app):
    log = logging.getLogger("http")

    @app.before_request
    def _inicio():
        g.t0 = time.perf_counter()
        g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex

    @app.after_request
    def _fin(respuesta):
        respuesta.headers["X-Request-ID"] = g.get("request_id", "")
        if not request.path.startswith("/health"):
            duracion = (time.perf_counter() - g.get("t0", time.perf_counter())) * 1000
            log.info(
                "peticion",
                extra={
                    "campos": {
                        "metodo": request.method,
                        "ruta": request.full_path.rstrip("?"),
                        "estado": respuesta.status_code,
                        "duracion_ms": round(duracion, 2),
                        "request_id": g.get("request_id"),
                        "usuario_id": request.headers.get("X-Usuario-Id"),
                    }
                },
            )
        return respuesta


class ParametroInvalido(ValueError):
    """Parámetro de consulta con formato incorrecto → 400."""


def registrar_errores(app):
    @app.errorhandler(ParametroInvalido)
    def _param(e):
        return jsonify(error="parametro_invalido", mensaje=str(e)), 400

    @app.errorhandler(405)
    def _metodo(e):
        return jsonify(error="metodo_no_permitido", mensaje=app.config.get("MENSAJE_405", str(e))), 405

    @app.errorhandler(HTTPException)
    def _http(e):
        return jsonify(error=e.name.lower().replace(" ", "_"), mensaje=e.description), e.code

    @app.errorhandler(Exception)
    def _general(e):
        logging.getLogger("http").exception("error no controlado")
        return jsonify(error="error_interno", mensaje="Error interno del servidor"), 500

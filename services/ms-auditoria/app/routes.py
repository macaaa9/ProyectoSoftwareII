"""API REST de ms-auditoria. Solo lectura: no hay POST, PUT ni DELETE (los registros llegan por eventos)."""
import math
import os

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from sqlalchemy import func, select, text

from .extensions import db
from .fechas import parsear_parametro
from .models import RegistroAuditoria as R
from .observabilidad import ParametroInvalido

bp = Blueprint("auditoria", __name__)
_STATIC = os.path.join(os.path.dirname(__file__), "static")


# ---------- salud (probes de Kubernetes y check de Consul) ----------
@bp.get("/health/live")
def vivo():
    return jsonify(estado="ok")


@bp.get("/health")
def salud():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(estado="ok", servicio=current_app.config["SERVICE_NAME"], bd="ok")
    except Exception as e:  # noqa: BLE001
        db.session.rollback()
        return jsonify(estado="error", bd=str(e.__class__.__name__)), 503


# ---------- documentación OpenAPI ----------
@bp.get("/openapi.yaml")
def openapi():
    return send_from_directory(_STATIC, "openapi.yaml", mimetype="application/yaml")


@bp.get("/docs")
def docs():
    return send_from_directory(_STATIC, "docs.html")


# ---------- helpers de parámetros ----------
def _entero(nombre, minimo=None, maximo=None, defecto=None):
    valor = request.args.get(nombre)
    if valor in (None, ""):
        return defecto
    try:
        n = int(valor)
    except ValueError:
        raise ParametroInvalido(f"'{nombre}' debe ser un número entero")
    if minimo is not None and n < minimo:
        raise ParametroInvalido(f"'{nombre}' debe ser >= {minimo}")
    if maximo is not None and n > maximo:
        n = maximo
    return n


def _fecha(nombre, fin_de_dia=False):
    valor = request.args.get(nombre)
    if not valor:
        return None
    try:
        return parsear_parametro(valor, current_app.config["APP_TZ"], fin_de_dia)
    except ValueError:
        raise ParametroInvalido(f"'{nombre}' debe tener formato YYYY-MM-DD o fecha-hora ISO 8601")


# ---------- consultas ----------
@bp.get("/auditoria")
def listar():
    cfg = current_app.config
    condiciones = []

    usuario = _entero("usuario", minimo=1)
    if usuario is not None:
        condiciones.append(R.usuario_id == usuario)
    producto = _entero("producto", minimo=1)
    if producto is not None:
        condiciones.append(R.producto_id == producto)
    tipo = (request.args.get("tipo") or "").strip().upper()
    if tipo:
        # ?tipo=SALIDA encuentra MOVIMIENTO_SALIDA; ?tipo=RECEPCION_MERCANCIA coincide exacto
        condiciones.append(R.tipo_operacion.in_([tipo, f"MOVIMIENTO_{tipo}"]))
    servicio = (request.args.get("servicio") or "").strip()
    if servicio:
        condiciones.append(R.servicio_origen == servicio)
    referencia = (request.args.get("referencia") or "").strip()
    if referencia:
        condiciones.append(R.referencia == referencia)

    if request.args.get("fecha"):  # un día completo, en hora local (APP_TZ)
        condiciones.append(R.fecha_hora >= _fecha("fecha"))
        condiciones.append(R.fecha_hora < _fecha("fecha", fin_de_dia=True))
    desde, hasta = _fecha("desde"), _fecha("hasta", fin_de_dia=True)
    if desde:
        condiciones.append(R.fecha_hora >= desde)
    if hasta:
        condiciones.append(R.fecha_hora < hasta)

    pagina = _entero("pagina", minimo=1, defecto=1)
    por_pagina = _entero("por_pagina", minimo=1, maximo=cfg["POR_PAGINA_MAX"], defecto=cfg["POR_PAGINA_DEFECTO"])

    total = db.session.scalar(select(func.count(R.id)).where(*condiciones))
    filas = db.session.scalars(
        select(R)
        .where(*condiciones)
        .order_by(R.fecha_hora.desc(), R.id.desc())
        .limit(por_pagina)
        .offset((pagina - 1) * por_pagina)
    ).all()

    return jsonify(
        datos=[f.to_dict() for f in filas],
        paginacion={
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total": total,
            "paginas": math.ceil(total / por_pagina) if total else 0,
        },
    )


@bp.get("/auditoria/<int:registro_id>")
def detalle(registro_id):
    registro = db.session.get(R, registro_id)
    if registro is None:
        return jsonify(error="no_encontrado", mensaje=f"No existe el registro {registro_id}"), 404
    return jsonify(registro.to_dict())


# Rutas explícitas para que PUT/PATCH/DELETE respondan 405 con mensaje claro (no 404)
@bp.route("/auditoria", methods=["POST", "PUT", "PATCH", "DELETE"])
@bp.route("/auditoria/<int:registro_id>", methods=["POST", "PUT", "PATCH", "DELETE"])
def inmutable(registro_id=None):
    return jsonify(error="metodo_no_permitido", mensaje=current_app.config["MENSAJE_405"]), 405

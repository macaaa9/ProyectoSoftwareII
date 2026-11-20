"""API REST de ms-reportes (solo lectura)."""
import math
import os

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from sqlalchemy import text

from . import consultas
from .eventos import ESTADOS_VALIDOS, normalizar_estado
from .extensions import db
from .fechas import parsear_parametro
from .observabilidad import ParametroInvalido

bp = Blueprint("reportes", __name__)
_STATIC = os.path.join(os.path.dirname(__file__), "static")


# ---------- salud y documentación ----------
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
        return jsonify(estado="error", bd=e.__class__.__name__), 503


@bp.get("/openapi.yaml")
def openapi():
    return send_from_directory(_STATIC, "openapi.yaml", mimetype="application/yaml")


@bp.get("/docs")
def docs():
    return send_from_directory(_STATIC, "docs.html")


# ---------- helpers ----------
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
    return min(n, maximo) if maximo is not None else n


def _estado():
    valor = request.args.get("estado")
    if not valor:
        return None
    estado = normalizar_estado(valor)
    if not estado:
        raise ParametroInvalido(f"'estado' debe ser uno de: {', '.join(ESTADOS_VALIDOS)} (o verde/amarillo/rojo)")
    return estado


def _rango():
    cfg = current_app.config
    desde_txt, hasta_txt = request.args.get("desde"), request.args.get("hasta")
    desde_def, hasta_def = consultas.rango_por_defecto(_entero("dias", 1, 366, cfg["DIAS_ROTACION"]))
    try:
        desde = parsear_parametro(desde_txt, cfg["APP_TZ"]) if desde_txt else desde_def
        hasta = parsear_parametro(hasta_txt, cfg["APP_TZ"], fin_de_dia=True) if hasta_txt else hasta_def
    except ValueError:
        raise ParametroInvalido("'desde' y 'hasta' deben tener formato YYYY-MM-DD")
    if desde >= hasta:
        raise ParametroInvalido("'desde' debe ser anterior a 'hasta'")
    return desde, hasta


# ---------- reportes ----------
@bp.get("/reportes/existencias")
def existencias():
    cfg = current_app.config
    pagina = _entero("pagina", 1, defecto=1)
    por_pagina = _entero("por_pagina", 1, cfg["POR_PAGINA_MAX"], cfg["POR_PAGINA_DEFECTO"])
    r = consultas.existencias(
        bodega=_entero("bodega", 1),
        estado=_estado(),
        producto=_entero("producto", 1),
        q=(request.args.get("q") or "").strip() or None,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    return jsonify(
        datos=r["datos"],
        resumen={"registros": r["total"], "unidades_totales": r["unidades_totales"]},
        paginacion={
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total": r["total"],
            "paginas": math.ceil(r["total"] / por_pagina) if r["total"] else 0,
        },
    )


@bp.get("/reportes/valorizacion")
def valorizacion():
    agrupar = request.args.get("agrupar", "producto")
    if agrupar not in ("producto", "bodega"):
        raise ParametroInvalido("'agrupar' debe ser 'producto' o 'bodega'")
    return jsonify(consultas.valorizacion(agrupar=agrupar, bodega=_entero("bodega", 1)))


@bp.get("/reportes/rotacion")
def rotacion():
    desde, hasta = _rango()
    limite = _entero("limite", 1, 100, 10)
    return jsonify(consultas.rotacion(desde, hasta, current_app.config["TIPOS_SALIDA"], limite))


@bp.get("/reportes/quiebres")
def quiebres():
    return jsonify(consultas.quiebres(bodega=_entero("bodega", 1)))


@bp.get("/reportes/dashboard")
def dashboard():
    cfg = current_app.config
    dias = _entero("dias", 1, 366, cfg["DIAS_ROTACION"])
    return jsonify(consultas.dashboard(cfg["TIPOS_SALIDA"], dias))


@bp.route("/reportes/<path:_ruta>", methods=["POST", "PUT", "PATCH", "DELETE"])
def solo_lectura(_ruta):
    return jsonify(error="metodo_no_permitido", mensaje=current_app.config["MENSAJE_405"]), 405

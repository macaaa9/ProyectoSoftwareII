"""Cálculo de los reportes (RF11, RF14, RF18) sobre la base de lectura."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select

from .extensions import db
from .fechas import iso_utc
from .models import ExistenciaRM as E
from .models import MovimientoRM as M
from .models import ProductoRM as P


def _num(valor):
    return round(float(valor or 0), 2)


def _solo_activos():
    # Una existencia sin producto en productos_rm se muestra (aún no llegó ProductoActualizado)
    return or_(P.activo.is_(None), P.activo.is_(True))


def _join_producto(stmt):
    return stmt.outerjoin(P, P.producto_id == E.producto_id)


# ---------------- existencias actuales ----------------
def existencias(bodega=None, estado=None, producto=None, q=None, pagina=1, por_pagina=50):
    condiciones = [_solo_activos()]
    if bodega is not None:
        condiciones.append(E.bodega_id == bodega)
    if estado:
        condiciones.append(E.estado == estado)
    if producto is not None:
        condiciones.append(E.producto_id == producto)
    if q:
        patron = f"%{q}%"
        condiciones.append(or_(P.nombre.ilike(patron), P.codigo.ilike(patron)))

    base = _join_producto(select(E, P).select_from(E)).where(*condiciones)
    total = db.session.scalar(_join_producto(select(func.count()).select_from(E)).where(*condiciones))
    unidades = db.session.scalar(
        _join_producto(select(func.coalesce(func.sum(E.cantidad), 0)).select_from(E)).where(*condiciones)
    )
    filas = db.session.execute(
        base.order_by(P.nombre, E.producto_id, E.bodega_id).limit(por_pagina).offset((pagina - 1) * por_pagina)
    ).all()

    datos = []
    for e, p in filas:
        precio = _num(p.precio) if p and p.precio is not None else None
        datos.append({
            "producto_id": e.producto_id,
            "codigo": p.codigo if p else None,
            "nombre": p.nombre if p else None,
            "bodega_id": e.bodega_id,
            "cantidad": e.cantidad,
            "estado": e.estado,
            "precio": precio,
            "valor": _num((precio or 0) * e.cantidad),
        })
    return {"datos": datos, "total": total, "unidades_totales": int(unidades or 0)}


# ---------------- valorización (cantidad × precio) ----------------
def valorizacion(agrupar="producto", bodega=None):
    valor = func.coalesce(func.sum(E.cantidad * func.coalesce(P.precio, 0)), 0)
    unidades = func.coalesce(func.sum(E.cantidad), 0)
    condiciones = [_solo_activos()]
    if bodega is not None:
        condiciones.append(E.bodega_id == bodega)

    if agrupar == "bodega":
        stmt = select(E.bodega_id, unidades, valor, func.count(E.producto_id.distinct())).select_from(E)
        filas = db.session.execute(
            _join_producto(stmt).where(*condiciones).group_by(E.bodega_id).order_by(valor.desc())
        ).all()
        datos = [{"bodega_id": b, "unidades": int(u), "valor": _num(v), "productos": int(n)}
                 for b, u, v, n in filas]
    else:
        stmt = select(E.producto_id, P.codigo, P.nombre, P.precio, unidades, valor).select_from(E)
        filas = db.session.execute(
            _join_producto(stmt).where(*condiciones)
            .group_by(E.producto_id, P.codigo, P.nombre, P.precio)
            .order_by(valor.desc())
        ).all()
        datos = [{"producto_id": pid, "codigo": cod, "nombre": nom,
                  "precio": _num(pre) if pre is not None else None,
                  "unidades": int(u), "valor": _num(v)}
                 for pid, cod, nom, pre, u, v in filas]

    sin_precio = db.session.scalar(
        _join_producto(select(func.count(E.producto_id.distinct())).select_from(E))
        .where(*condiciones, P.precio.is_(None))
    )
    return {
        "agrupado_por": agrupar,
        "valor_total": _num(sum(d["valor"] for d in datos)),
        "unidades_totales": sum(d["unidades"] for d in datos),
        "productos_sin_precio": int(sin_precio or 0),
        "datos": datos,
    }


# ---------------- rotación ----------------
def rango_por_defecto(dias):
    hasta = datetime.now(timezone.utc).replace(tzinfo=None)
    return hasta - timedelta(days=dias), hasta


def rotacion(desde, hasta, tipos_salida, limite=10):
    """Unidades vendidas en el periodo. indice_rotacion = unidades_salida / stock_actual."""
    salidas = dict(db.session.execute(
        select(M.producto_id, func.sum(M.cantidad))
        .where(M.tipo.in_(tipos_salida), M.fecha >= desde, M.fecha < hasta)
        .group_by(M.producto_id)
    ).all())
    stock = dict(db.session.execute(
        select(E.producto_id, func.sum(E.cantidad)).group_by(E.producto_id)
    ).all())
    productos = {p.producto_id: p for p in db.session.scalars(select(P).where(P.activo.is_(True)))}

    items = []
    for pid in set(productos) | set(salidas):
        p = productos.get(pid)
        if p is None and pid not in stock:
            continue
        unidades = int(salidas.get(pid) or 0)
        actual = int(stock.get(pid) or 0)
        items.append({
            "producto_id": pid,
            "codigo": p.codigo if p else None,
            "nombre": p.nombre if p else None,
            "unidades_salida": unidades,
            "stock_actual": actual,
            "indice_rotacion": round(unidades / actual, 2) if actual > 0 else None,
        })

    mayor = sorted((i for i in items if i["unidades_salida"] > 0),
                   key=lambda i: (-i["unidades_salida"], i["producto_id"]))
    menor = sorted(items, key=lambda i: (i["unidades_salida"], -i["stock_actual"], i["producto_id"]))
    return {
        "desde": iso_utc(desde),
        "hasta": iso_utc(hasta),
        "productos_analizados": len(items),
        "mayor_rotacion": mayor[:limite],
        "menor_rotacion": menor[:limite],
    }


# ---------------- quiebres de stock ----------------
def quiebres(bodega=None):
    condiciones = [_solo_activos()]
    if bodega is not None:
        condiciones.append(E.bodega_id == bodega)
    total = db.session.scalar(_join_producto(select(func.count()).select_from(E)).where(*condiciones))
    filas = db.session.execute(
        _join_producto(select(E, P).select_from(E))
        .where(*condiciones, E.estado == "agotado").order_by(P.nombre)
    ).all()
    sin_stock_total = db.session.scalar(
        select(func.count()).select_from(
            _join_producto(select(E.producto_id).select_from(E))
            .where(_solo_activos())
            .group_by(E.producto_id)
            .having(func.sum(E.cantidad) <= 0)
            .subquery()
        )
    )
    en_quiebre = len(filas)
    return {
        "registros_evaluados": total,
        "en_quiebre": en_quiebre,
        "porcentaje_quiebre": round(en_quiebre * 100 / total, 2) if total else 0.0,
        "productos_sin_stock_en_ninguna_bodega": int(sin_stock_total or 0),
        "datos": [{
            "producto_id": e.producto_id,
            "codigo": p.codigo if p else None,
            "nombre": p.nombre if p else None,
            "bodega_id": e.bodega_id,
            "desde": iso_utc(e.actualizado_en),
        } for e, p in filas],
    }


# ---------------- semáforo y dashboard ----------------
def resumen_semaforo():
    filas = db.session.execute(
        _join_producto(select(E.estado, func.count()).select_from(E))
        .where(_solo_activos()).group_by(E.estado)
    ).all()
    resumen = {"disponible": 0, "stock_bajo": 0, "agotado": 0}
    for estado, n in filas:
        if estado in resumen:
            resumen[estado] = int(n)
    return resumen


def dashboard(tipos_salida, dias):
    desde, hasta = rango_por_defecto(dias)
    val = valorizacion()
    q = quiebres()
    rot = rotacion(desde, hasta, tipos_salida, limite=5)
    productos_activos = db.session.scalar(select(func.count()).select_from(P).where(P.activo.is_(True)))
    return {
        "valor_total_inventario": val["valor_total"],
        "unidades_totales": val["unidades_totales"],
        "productos_activos": int(productos_activos or 0),
        "productos_sin_precio": val["productos_sin_precio"],
        "semaforo": resumen_semaforo(),
        "quiebres": {"en_quiebre": q["en_quiebre"], "porcentaje_quiebre": q["porcentaje_quiebre"]},
        "rotacion": {"periodo_dias": dias, "top_mayor": rot["mayor_rotacion"], "top_menor": rot["menor_rotacion"]},
    }

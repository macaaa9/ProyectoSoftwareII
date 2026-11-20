"""Proyecciones: aplica cada evento sobre la base de lectura.
Idempotente: un movimiento repetido no se cuenta dos veces y un evento viejo no pisa datos nuevos."""
import logging
from decimal import Decimal, InvalidOperation

from sqlalchemy import select

from .eventos import EventoInvalido, decodificar, entero, id_evento, normalizar_estado, tipo_de
from .extensions import db
from .fechas import parsear_fecha_evento
from .models import ExistenciaRM, MovimientoRM, ProductoRM

log = logging.getLogger("reportes")


def _es_viejo(fila, fecha):
    return fila.actualizado_en is not None and fecha < fila.actualizado_en


def _precio(valor):
    if valor in (None, ""):
        return None
    try:
        return Decimal(str(valor)).quantize(Decimal("0.01"))
    except InvalidOperation:
        raise EventoInvalido(f"precio inválido: {valor!r}")


def aplicar_producto(datos, fecha):
    pid = entero(datos.get("producto_id") or datos.get("id"), "producto_id", requerido=True)
    p = db.session.get(ProductoRM, pid)
    if p is None:
        p = ProductoRM(producto_id=pid, activo=True)
        db.session.add(p)
    elif _es_viejo(p, fecha):
        return "ignorado_viejo"
    if "codigo" in datos:
        p.codigo = str(datos["codigo"])[:50]
    if "nombre" in datos:
        p.nombre = str(datos["nombre"])[:200]
    if "precio" in datos:
        p.precio = _precio(datos["precio"])
    if "activo" in datos:
        p.activo = bool(datos["activo"])
    p.actualizado_en = fecha
    return "producto"


def aplicar_existencia(producto_id, bodega_id, cantidad, estado, fecha):
    e = db.session.get(ExistenciaRM, (producto_id, bodega_id))
    if e is None:
        e = ExistenciaRM(producto_id=producto_id, bodega_id=bodega_id, cantidad=0)
        db.session.add(e)
    elif _es_viejo(e, fecha):
        return False
    if cantidad is not None:
        e.cantidad = cantidad
    nuevo = normalizar_estado(estado)
    if nuevo:
        e.estado = nuevo
    elif e.cantidad <= 0:
        e.estado = "agotado"
    elif e.estado in (None, "agotado"):
        e.estado = "disponible"  # sin mínimo conocido; EstadoStockCambiado lo corrige
    e.actualizado_en = fecha
    return True


def aplicar_movimiento(datos, fecha, evento_id):
    if db.session.scalar(select(MovimientoRM.id).where(MovimientoRM.evento_id == evento_id)):
        return "duplicado"
    producto = entero(datos.get("producto_id"), "producto_id", requerido=True)
    cantidad = entero(datos.get("cantidad"), "cantidad", requerido=True)
    tipo = str(datos.get("tipo") or "desconocido").strip().lower()[:30]
    bodega = entero(datos.get("bodega_origen_id") or datos.get("bodega_id")
                    or datos.get("bodega_destino_id"), "bodega_id")
    db.session.add(MovimientoRM(
        evento_id=evento_id,
        movimiento_id=entero(datos.get("movimiento_id"), "movimiento_id"),
        producto_id=producto, bodega_id=bodega, tipo=tipo,
        cantidad=abs(cantidad), fecha=fecha,
    ))
    # Saldo resultante de cada bodega afectada (un traslado trae dos)
    saldos = datos.get("saldos")
    if not saldos and datos.get("cantidad_nueva") is not None and bodega is not None:
        saldos = [{"bodega_id": bodega, "cantidad": datos["cantidad_nueva"], "estado": datos.get("estado")}]
    for s in saldos or []:
        if not isinstance(s, dict):
            raise EventoInvalido("cada elemento de 'saldos' debe ser un objeto")
        aplicar_existencia(
            producto,
            entero(s.get("bodega_id"), "saldos[].bodega_id", requerido=True),
            entero(s.get("cantidad"), "saldos[].cantidad", requerido=True),
            s.get("estado"), fecha,
        )
    return "movimiento"


def procesar_mensaje(cuerpo, routing_key=None):
    """Lanza EventoInvalido (-> DLQ) o SQLAlchemyError (-> reintento)."""
    evento, datos = decodificar(cuerpo)
    tipo = tipo_de(evento, routing_key)
    try:
        fecha = parsear_fecha_evento(evento.get("fecha") or datos.get("fecha"))
    except ValueError:
        raise EventoInvalido(f"fecha inválida: {evento.get('fecha')!r}")
    try:
        if tipo in ("ProductoActualizado", "ProductoCreado"):
            resultado = aplicar_producto(datos, fecha)
        elif tipo == "MovimientoRegistrado":
            resultado = aplicar_movimiento(datos, fecha, id_evento(evento, cuerpo))
        elif tipo == "EstadoStockCambiado":
            ok = aplicar_existencia(
                entero(datos.get("producto_id"), "producto_id", requerido=True),
                entero(datos.get("bodega_id"), "bodega_id", requerido=True),
                entero(datos.get("cantidad"), "cantidad"),
                datos.get("estado"), fecha,
            )
            resultado = "existencia" if ok else "ignorado_viejo"
        else:
            log.info(f"evento ignorado: {tipo}")
            return "ignorado"
        db.session.commit()
        return resultado
    except EventoInvalido:
        db.session.rollback()
        raise

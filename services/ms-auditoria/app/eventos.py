"""Traduce los eventos del bus (ver docs/CONTRATO_EVENTOS.md) a filas de registros_auditoria.

Funciones puras: no tocan la BD, así se prueban fácilmente.
"""
import hashlib
import json

from .fechas import parsear_fecha_evento

TIPO_POR_ROUTING_KEY = {
    "inventario.movimiento.registrado": "MovimientoRegistrado",
    "compras.mercancia.recibida": "MercanciaRecibida",
    "compras.devolucion.registrada": "DevolucionProveedorRegistrada",
}


class EventoInvalido(ValueError):
    """El mensaje no se puede procesar nunca (JSON roto, faltan campos). Va a la cola de errores (DLQ)."""


def _entero(valor, campo, requerido=False):
    if valor is None or valor == "":
        if requerido:
            raise EventoInvalido(f"falta el campo '{campo}'")
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise EventoInvalido(f"'{campo}' debe ser un entero (llegó {valor!r})")


def _texto(valor, largo):
    if valor is None:
        return None
    return str(valor)[:largo]


def decodificar(cuerpo):
    try:
        evento = json.loads(cuerpo)
    except (ValueError, UnicodeDecodeError) as e:
        raise EventoInvalido(f"el mensaje no es JSON válido: {e}")
    if not isinstance(evento, dict):
        raise EventoInvalido("el mensaje debe ser un objeto JSON")
    return evento


def id_evento(evento, cuerpo):
    """Usa evento_id del mensaje; si no viene, un hash del contenido (misma reentrega → mismo id)."""
    valor = evento.get("evento_id") or evento.get("id")
    if valor:
        return str(valor)[:90]
    datos = cuerpo if isinstance(cuerpo, bytes) else str(cuerpo).encode()
    return hashlib.sha256(datos).hexdigest()


def construir_registros(evento, routing_key=None, evento_id=None):
    tipo = evento.get("tipo") or evento.get("evento") or TIPO_POR_ROUTING_KEY.get(routing_key or "")
    datos = evento.get("datos") or evento.get("data") or {}
    if not isinstance(datos, dict):
        raise EventoInvalido("'datos' debe ser un objeto")
    base_id = evento_id or id_evento(evento, json.dumps(evento, sort_keys=True))
    try:
        fecha = parsear_fecha_evento(evento.get("fecha") or datos.get("fecha"))
    except ValueError:
        raise EventoInvalido(f"fecha inválida: {evento.get('fecha')!r}")
    origen = evento.get("servicio_origen")

    if tipo == "MovimientoRegistrado":
        tipo_mov = str(datos.get("tipo") or "desconocido").strip().upper()
        mov_id = datos.get("movimiento_id")
        return [
            {
                "evento_id": base_id,
                "usuario_id": _entero(datos.get("usuario_id"), "usuario_id"),
                "fecha_hora": fecha,
                "servicio_origen": _texto(origen or "ms-inventario", 50),
                "tipo_operacion": _texto(f"MOVIMIENTO_{tipo_mov}", 50),
                "producto_id": _entero(datos.get("producto_id"), "producto_id", requerido=True),
                "cantidad_anterior": _entero(datos.get("cantidad_anterior"), "cantidad_anterior"),
                "cantidad_modificada": _entero(datos.get("cantidad"), "cantidad", requerido=True),
                "motivo": _texto(datos.get("motivo"), 255),
                "referencia": _texto(datos.get("referencia") or (f"MOV-{mov_id}" if mov_id else None), 100),
            }
        ]

    if tipo == "MercanciaRecibida":
        items = datos.get("items") or []
        if not isinstance(items, list) or not items:
            raise EventoInvalido("MercanciaRecibida requiere una lista 'items' no vacía")
        orden_id = datos.get("orden_id")
        referencia = datos.get("referencia") or (f"OC-{orden_id}" if orden_id else None)
        usuario = _entero(datos.get("usuario_id"), "usuario_id")
        registros = []
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise EventoInvalido("cada item debe ser un objeto")
            registros.append(
                {
                    "evento_id": f"{base_id}#{i}",
                    "usuario_id": usuario,
                    "fecha_hora": fecha,
                    "servicio_origen": _texto(origen or "ms-compras", 50),
                    "tipo_operacion": "RECEPCION_MERCANCIA",
                    "producto_id": _entero(item.get("producto_id"), "items[].producto_id", requerido=True),
                    "cantidad_anterior": _entero(item.get("cantidad_anterior"), "items[].cantidad_anterior"),
                    "cantidad_modificada": _entero(item.get("cantidad"), "items[].cantidad", requerido=True),
                    "motivo": _texto(datos.get("motivo") or "Recepción de orden de compra", 255),
                    "referencia": _texto(referencia, 100),
                }
            )
        return registros

    if tipo == "DevolucionProveedorRegistrada":
        dev_id, orden_id = datos.get("devolucion_id"), datos.get("orden_id")
        referencia = datos.get("referencia") or (
            f"DEV-{dev_id}" if dev_id else (f"OC-{orden_id}" if orden_id else None)
        )
        return [
            {
                "evento_id": base_id,
                "usuario_id": _entero(datos.get("usuario_id"), "usuario_id"),
                "fecha_hora": fecha,
                "servicio_origen": _texto(origen or "ms-compras", 50),
                "tipo_operacion": "DEVOLUCION_PROVEEDOR",
                "producto_id": _entero(datos.get("producto_id"), "producto_id", requerido=True),
                "cantidad_anterior": _entero(datos.get("cantidad_anterior"), "cantidad_anterior"),
                "cantidad_modificada": _entero(datos.get("cantidad"), "cantidad", requerido=True),
                "motivo": _texto(datos.get("motivo"), 255),
                "referencia": _texto(referencia, 100),
            }
        ]

    return []  # tipo que este servicio no audita: se ignora

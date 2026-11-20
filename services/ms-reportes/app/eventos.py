"""Decodificación y validación de los eventos (ver docs/CONTRATO_EVENTOS.md)."""
import hashlib
import json

TIPO_POR_ROUTING_KEY = {
    "catalogo.producto.actualizado": "ProductoActualizado",
    "inventario.movimiento.registrado": "MovimientoRegistrado",
    "inventario.estado_stock.cambiado": "EstadoStockCambiado",
}

_ESTADOS = {
    "disponible": "disponible", "verde": "disponible",
    "stock_bajo": "stock_bajo", "bajo": "stock_bajo", "amarillo": "stock_bajo",
    "agotado": "agotado", "rojo": "agotado",
}
ESTADOS_VALIDOS = ("disponible", "stock_bajo", "agotado")


class EventoInvalido(ValueError):
    """Mensaje irrecuperable (JSON roto, faltan campos). Se envía a la cola de errores (DLQ)."""


def normalizar_estado(valor):
    """'Stock bajo', 'amarillo', 'STOCK_BAJO' -> 'stock_bajo'. None si no se reconoce."""
    if not valor:
        return None
    clave = str(valor).strip().lower().replace(" ", "_").replace("-", "_")
    return _ESTADOS.get(clave)


def entero(valor, campo, requerido=False):
    if valor is None or valor == "":
        if requerido:
            raise EventoInvalido(f"falta el campo '{campo}'")
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise EventoInvalido(f"'{campo}' debe ser un entero (llegó {valor!r})")


def decodificar(cuerpo):
    try:
        evento = json.loads(cuerpo)
    except (ValueError, UnicodeDecodeError) as e:
        raise EventoInvalido(f"el mensaje no es JSON válido: {e}")
    if not isinstance(evento, dict):
        raise EventoInvalido("el mensaje debe ser un objeto JSON")
    datos = evento.get("datos") or evento.get("data") or {}
    if not isinstance(datos, dict):
        raise EventoInvalido("'datos' debe ser un objeto")
    return evento, datos


def tipo_de(evento, routing_key):
    return evento.get("tipo") or evento.get("evento") or TIPO_POR_ROUTING_KEY.get(routing_key or "")


def id_evento(evento, cuerpo):
    """evento_id del mensaje; si no viene, hash del contenido (misma reentrega -> mismo id)."""
    valor = evento.get("evento_id") or evento.get("id")
    if valor:
        return str(valor)[:100]
    datos = cuerpo if isinstance(cuerpo, bytes) else str(cuerpo).encode()
    return hashlib.sha256(datos).hexdigest()

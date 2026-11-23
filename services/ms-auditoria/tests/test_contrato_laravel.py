"""Contrato con el publicador Laravel de ms-inventory (app/Services/EventPublisher.php)."""
import json

from app.models import RegistroAuditoria
from app.servicio import procesar_mensaje


def test_movimiento_desde_ms_inventory_queda_auditado(app):
    cuerpo = json.dumps({
        "evento_id": "laravel-mov-15",
        "tipo": "MovimientoRegistrado",
        "servicio_origen": "ms-inventory",
        "fecha": "2026-11-22T15:00:00Z",
        "datos": {"movimiento_id": 15, "producto_id": 7, "bodega_id": 1, "tipo": "salida", "cantidad": 25,
                  "cantidad_anterior": 30, "cantidad_nueva": 5, "estado": "stock_bajo", "motivo": "Venta",
                  "referencia": None, "usuario_id": 3},
    })
    assert procesar_mensaje(cuerpo, "inventario.movimiento.registrado") == 1
    r = RegistroAuditoria.query.one()
    assert (r.servicio_origen, r.tipo_operacion, r.cantidad_anterior, r.cantidad_modificada, r.usuario_id) == \
        ("ms-inventory", "MOVIMIENTO_SALIDA", 30, 25, 3)
    assert r.referencia == "MOV-15"
    # Reentrega del mismo mensaje: no se duplica
    assert procesar_mensaje(cuerpo, "inventario.movimiento.registrado") == 0

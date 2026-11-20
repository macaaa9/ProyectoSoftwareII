import json

import pytest

from app.eventos import EventoInvalido, construir_registros
from app.models import RegistroAuditoria
from app.servicio import procesar_mensaje

MOVIMIENTO = {
    "evento_id": "ev-1",
    "tipo": "MovimientoRegistrado",
    "servicio_origen": "ms-inventario",
    "fecha": "2026-11-19T20:00:00Z",
    "datos": {
        "movimiento_id": 981,
        "tipo": "salida",
        "producto_id": 42,
        "bodega_origen_id": 1,
        "cantidad": 5,
        "cantidad_anterior": 30,
        "motivo": "Venta mostrador",
        "usuario_id": 7,
    },
}


def test_movimiento_genera_un_registro():
    (r,) = construir_registros(MOVIMIENTO, evento_id="ev-1")
    assert r["tipo_operacion"] == "MOVIMIENTO_SALIDA"
    assert r["producto_id"] == 42 and r["cantidad_modificada"] == 5 and r["cantidad_anterior"] == 30
    assert r["usuario_id"] == 7 and r["referencia"] == "MOV-981"
    assert r["fecha_hora"].isoformat() == "2026-11-19T20:00:00"


def test_mercancia_recibida_un_registro_por_item():
    evento = {
        "tipo": "MercanciaRecibida",
        "fecha": "2026-11-19 10:00:00",  # formato Laravel
        "datos": {"orden_id": 15, "usuario_id": 3, "items": [{"producto_id": 1, "cantidad": 10}, {"producto_id": 2, "cantidad": 4}]},
    }
    regs = construir_registros(evento, evento_id="ev-2")
    assert [r["evento_id"] for r in regs] == ["ev-2#0", "ev-2#1"]
    assert all(r["referencia"] == "OC-15" and r["tipo_operacion"] == "RECEPCION_MERCANCIA" for r in regs)
    assert regs[0]["servicio_origen"] == "ms-compras"


def test_tipo_por_routing_key_si_no_viene_en_el_mensaje():
    evento = {"datos": {"producto_id": 9, "cantidad": 2, "devolucion_id": 4}}
    (r,) = construir_registros(evento, routing_key="compras.devolucion.registrada", evento_id="x")
    assert r["tipo_operacion"] == "DEVOLUCION_PROVEEDOR" and r["referencia"] == "DEV-4"


def test_evento_sin_producto_es_invalido():
    with pytest.raises(EventoInvalido):
        construir_registros({"tipo": "MovimientoRegistrado", "datos": {"cantidad": 1}}, evento_id="x")


def test_evento_desconocido_se_ignora():
    assert construir_registros({"tipo": "ProductoActualizado", "datos": {}}, evento_id="x") == []


def test_json_invalido(app):
    with pytest.raises(EventoInvalido):
        procesar_mensaje(b"{no es json")


def test_reentrega_no_duplica(app):
    cuerpo = json.dumps(MOVIMIENTO).encode()
    assert procesar_mensaje(cuerpo, "inventario.movimiento.registrado") == 1
    assert procesar_mensaje(cuerpo, "inventario.movimiento.registrado") == 0
    assert RegistroAuditoria.query.count() == 1


def test_sin_evento_id_usa_hash_del_contenido(app):
    sin_id = {k: v for k, v in MOVIMIENTO.items() if k != "evento_id"}
    cuerpo = json.dumps(sin_id).encode()
    assert procesar_mensaje(cuerpo) == 1
    assert procesar_mensaje(cuerpo) == 0

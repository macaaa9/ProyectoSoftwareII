"""Contrato con los publicadores Laravel (ms-inventory y ms-catalog, app/Services/EventPublisher.php).
Los mensajes tienen exactamente la forma que arma el PHP."""
import json

from app.extensions import db
from app.models import ExistenciaRM, MovimientoRM, ProductoRM
from app.servicio import procesar_mensaje


def _msg(tipo, datos, origen, fecha="2026-11-22T15:00:00Z", eid="laravel-1"):
    return json.dumps({"evento_id": eid, "tipo": tipo, "servicio_origen": origen, "fecha": fecha, "datos": datos})


def test_producto_desde_ms_catalog(app):
    # Eloquent serializa decimal:2 como texto ("2500.00")
    cuerpo = _msg("ProductoActualizado", {"producto_id": 7, "codigo": "P-7", "nombre": "Cuaderno",
                                          "precio": "2500.00", "activo": True}, "ms-catalog")
    assert procesar_mensaje(cuerpo, "catalogo.producto.actualizado") == "producto"
    p = db.session.get(ProductoRM, 7)
    assert p.nombre == "Cuaderno" and str(p.precio) == "2500.00"


def test_movimiento_salida_desde_ms_inventory(app):
    procesar_mensaje(_msg("EstadoStockCambiado", {"producto_id": 7, "bodega_id": 1, "cantidad": 30,
                                                  "estado": "disponible"}, "ms-inventory",
                          fecha="2026-11-22T14:00:00Z", eid="laravel-0"), "inventario.estado_stock.cambiado")
    datos = {"movimiento_id": 15, "producto_id": 7, "bodega_id": 1, "tipo": "salida", "cantidad": 25,
             "cantidad_anterior": 30, "cantidad_nueva": 5, "estado": "stock_bajo", "motivo": "Venta",
             "referencia": None, "usuario_id": None}
    assert procesar_mensaje(_msg("MovimientoRegistrado", datos, "ms-inventory"),
                            "inventario.movimiento.registrado") == "movimiento"
    e = db.session.get(ExistenciaRM, (7, 1))
    assert e.cantidad == 5 and e.estado == "stock_bajo"
    assert db.session.query(MovimientoRM).filter_by(producto_id=7, tipo="salida").count() == 1

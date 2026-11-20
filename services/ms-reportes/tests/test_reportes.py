import json
from datetime import datetime, timedelta, timezone

import pytest

from app.eventos import EventoInvalido
from app.extensions import db
from app.models import ExistenciaRM, MovimientoRM
from app.servicio import procesar_mensaje

AHORA = datetime.now(timezone.utc).replace(microsecond=0)


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def ev(tipo, datos, eid=None, fecha=None):
    cuerpo = {"tipo": tipo, "fecha": _iso(fecha or AHORA), "datos": datos}
    if eid:
        cuerpo["evento_id"] = eid
    return json.dumps(cuerpo).encode()


def producto(pid, codigo, nombre, precio, activo=True):
    procesar_mensaje(ev("ProductoActualizado", {"producto_id": pid, "codigo": codigo, "nombre": nombre, "precio": precio, "activo": activo}))


def venta(eid, pid, cantidad, saldo, estado, bodega=1, dias_atras=1):
    return procesar_mensaje(ev("MovimientoRegistrado", {
        "tipo": "salida", "producto_id": pid, "bodega_origen_id": bodega, "cantidad": cantidad,
        "saldos": [{"bodega_id": bodega, "cantidad": saldo, "estado": estado}],
    }, eid=eid, fecha=AHORA - timedelta(days=dias_atras)))


@pytest.fixture
def datos(app):
    producto(1, "CUA-100", "Cuaderno 100 hojas", 4500)
    producto(2, "LAP-AZ", "Lapicero azul", 1200)
    producto(3, "BOR-01", "Borrador", 800)
    producto(4, "OLD-1", "Producto dado de baja", 100, activo=False)
    hace10 = AHORA - timedelta(days=10)
    procesar_mensaje(ev("EstadoStockCambiado", {"producto_id": 1, "bodega_id": 1, "cantidad": 40, "estado": "disponible"}, fecha=hace10))
    procesar_mensaje(ev("EstadoStockCambiado", {"producto_id": 2, "bodega_id": 1, "cantidad": 10, "estado": "disponible"}, fecha=hace10))
    procesar_mensaje(ev("EstadoStockCambiado", {"producto_id": 3, "bodega_id": 2, "cantidad": 5, "estado": "amarillo"}, fecha=hace10))
    procesar_mensaje(ev("EstadoStockCambiado", {"producto_id": 4, "bodega_id": 1, "cantidad": 99, "estado": "disponible"}, fecha=hace10))
    venta("v1", 1, 15, 25, "disponible")               # cuaderno: 40 -> 25
    venta("v2", 2, 10, 0, "rojo")                      # lapicero: 10 -> 0 (agotado)
    venta("v3", 1, 5, 20, "disponible", dias_atras=60)  # evento viejo: no pisa el saldo


# ------------------ proyecciones ------------------
def test_movimiento_actualiza_existencia_y_semaforo(datos):
    assert db.session.get(ExistenciaRM, (1, 1)).cantidad == 25
    e2 = db.session.get(ExistenciaRM, (2, 1))
    assert (e2.cantidad, e2.estado) == (0, "agotado")
    assert db.session.get(ExistenciaRM, (3, 2)).estado == "stock_bajo"


def test_movimiento_reentregado_no_se_cuenta_dos_veces(datos):
    assert venta("v1", 1, 15, 25, "disponible") == "duplicado"
    assert MovimientoRM.query.filter_by(evento_id="v1").count() == 1


def test_traslado_actualiza_dos_bodegas(app):
    procesar_mensaje(ev("MovimientoRegistrado", {
        "tipo": "traslado", "producto_id": 7, "bodega_origen_id": 1, "bodega_destino_id": 2, "cantidad": 3,
        "saldos": [{"bodega_id": 1, "cantidad": 7, "estado": "disponible"}, {"bodega_id": 2, "cantidad": 3, "estado": "stock_bajo"}],
    }, eid="t1"))
    assert db.session.get(ExistenciaRM, (7, 1)).cantidad == 7
    assert db.session.get(ExistenciaRM, (7, 2)).estado == "stock_bajo"


def test_evento_invalido(app):
    with pytest.raises(EventoInvalido):
        procesar_mensaje(ev("MovimientoRegistrado", {"tipo": "salida", "cantidad": 2}))
    with pytest.raises(EventoInvalido):
        procesar_mensaje(b"no-json")


def test_evento_desconocido(app):
    assert procesar_mensaje(ev("RecuperacionSolicitada", {})) == "ignorado"


# ------------------ endpoints ------------------
def test_existencias(client, datos):
    r = client.get("/reportes/existencias").get_json()
    assert r["resumen"]["registros"] == 3  # el producto inactivo no aparece
    assert client.get("/reportes/existencias?estado=rojo").get_json()["datos"][0]["producto_id"] == 2
    assert client.get("/reportes/existencias?q=cuader").get_json()["datos"][0]["valor"] == 25 * 4500
    assert client.get("/reportes/existencias?estado=morado").status_code == 400


def test_valorizacion(client, datos):
    r = client.get("/reportes/valorizacion").get_json()
    assert r["valor_total"] == 25 * 4500 + 0 * 1200 + 5 * 800
    b = client.get("/reportes/valorizacion?agrupar=bodega").get_json()
    assert {d["bodega_id"]: d["valor"] for d in b["datos"]} == {1: 112500.0, 2: 4000.0}
    assert client.get("/reportes/valorizacion?agrupar=x").status_code == 400


def test_rotacion(client, datos):
    r = client.get("/reportes/rotacion").get_json()
    assert [i["producto_id"] for i in r["mayor_rotacion"]] == [1, 2]
    assert r["mayor_rotacion"][0]["indice_rotacion"] == round(15 / 25, 2)
    assert r["menor_rotacion"][0]["producto_id"] == 3
    assert client.get("/reportes/rotacion?dias=90").get_json()["mayor_rotacion"][0]["unidades_salida"] == 20
    assert client.get("/reportes/rotacion?desde=2026-12-01&hasta=2026-11-01").status_code == 400


def test_quiebres_y_dashboard(client, datos):
    q = client.get("/reportes/quiebres").get_json()
    assert q["en_quiebre"] == 1 and q["productos_sin_stock_en_ninguna_bodega"] == 1
    d = client.get("/reportes/dashboard").get_json()
    assert d["semaforo"] == {"disponible": 1, "stock_bajo": 1, "agotado": 1}
    assert d["valor_total_inventario"] == 116500.0 and d["productos_activos"] == 3


def test_solo_lectura_health_docs(client):
    assert client.post("/reportes/existencias").status_code == 405
    assert client.get("/health").status_code == 200
    assert client.get("/docs").status_code == 200

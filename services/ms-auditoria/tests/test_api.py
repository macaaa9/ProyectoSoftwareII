import json

import pytest

from app.extensions import db
from app.models import RegistroAuditoria, RegistroInmutableError
from app.servicio import procesar_mensaje


def _mov(eid, producto, tipo, fecha, usuario=1):
    return json.dumps(
        {
            "evento_id": eid,
            "tipo": "MovimientoRegistrado",
            "fecha": fecha,
            "datos": {"producto_id": producto, "tipo": tipo, "cantidad": 2, "usuario_id": usuario},
        }
    ).encode()


@pytest.fixture
def datos(app):
    procesar_mensaje(_mov("a", 1, "salida", "2026-11-18T15:00:00Z", usuario=7))
    procesar_mensaje(_mov("b", 1, "entrada", "2026-11-19T15:00:00Z"))
    procesar_mensaje(_mov("c", 2, "salida", "2026-11-20T03:00:00Z"))  # 19-nov 22:00 en Colombia


def test_listar_y_paginar(client, datos):
    r = client.get("/auditoria?por_pagina=2").get_json()
    assert r["paginacion"] == {"pagina": 1, "por_pagina": 2, "total": 3, "paginas": 2}
    assert r["datos"][0]["evento_id"] == "c"  # más reciente primero


def test_filtros(client, datos):
    assert client.get("/auditoria?usuario=7").get_json()["paginacion"]["total"] == 1
    assert client.get("/auditoria?producto=1").get_json()["paginacion"]["total"] == 2
    assert client.get("/auditoria?tipo=salida").get_json()["paginacion"]["total"] == 2


def test_filtro_fecha_en_hora_colombia(client, datos):
    ids = {d["evento_id"] for d in client.get("/auditoria?fecha=2026-11-19").get_json()["datos"]}
    assert ids == {"b", "c"}


def test_parametro_invalido(client):
    assert client.get("/auditoria?usuario=abc").status_code == 400
    assert client.get("/auditoria?fecha=19/11/2026").status_code == 400


def test_detalle_y_404(client, datos):
    rid = client.get("/auditoria").get_json()["datos"][0]["id"]
    assert client.get(f"/auditoria/{rid}").status_code == 200
    assert client.get("/auditoria/99999").status_code == 404


@pytest.mark.parametrize("metodo", ["put", "patch", "delete", "post"])
def test_inmutable_por_api(client, datos, metodo):
    r = getattr(client, metodo)("/auditoria/1", json={})
    assert r.status_code == 405
    assert "inmutables" in r.get_json()["mensaje"]


def test_inmutable_por_orm(app, datos):
    reg = db.session.get(RegistroAuditoria, 1)
    reg.motivo = "cambiado"
    with pytest.raises(RegistroInmutableError):
        db.session.commit()
    db.session.rollback()


def test_health_y_docs(client):
    assert client.get("/health").get_json()["estado"] == "ok"
    assert client.get("/health/live").status_code == 200
    assert client.get("/openapi.yaml").status_code == 200
    assert client.get("/docs").status_code == 200

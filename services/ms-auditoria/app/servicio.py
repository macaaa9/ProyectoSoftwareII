"""Lógica de guardado, separada del transporte (RabbitMQ) para poder probarla sin broker."""
import logging

from sqlalchemy.exc import IntegrityError

from .eventos import construir_registros, decodificar, id_evento
from .extensions import db
from .models import RegistroAuditoria

log = logging.getLogger("auditoria")


def procesar_mensaje(cuerpo, routing_key=None):
    """Devuelve cuántas filas se insertaron (0 si el evento se ignora o ya estaba guardado).
    Lanza EventoInvalido si el mensaje es irrecuperable y SQLAlchemyError si falla la BD."""
    evento = decodificar(cuerpo)
    registros = construir_registros(evento, routing_key, id_evento(evento, cuerpo))
    if not registros:
        log.info("evento ignorado", extra={"campos": {"tipo": evento.get("tipo"), "routing_key": routing_key}})
        return 0
    try:
        db.session.add_all([RegistroAuditoria(**r) for r in registros])
        db.session.commit()  # todas las filas de un evento se guardan juntas o ninguna
    except IntegrityError:
        db.session.rollback()
        log.info("evento duplicado, ya auditado", extra={"campos": {"evento_id": registros[0]["evento_id"]}})
        return 0
    return len(registros)

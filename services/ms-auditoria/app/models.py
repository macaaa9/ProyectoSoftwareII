"""Modelo de db_auditoria. La tabla es de solo inserción (RNF18)."""
from datetime import datetime, timezone

from sqlalchemy import event

from .extensions import db
from .fechas import iso_utc

# BIGINT en MySQL; INTEGER en SQLite (para que el autoincremento funcione en las pruebas)
BigId = db.BigInteger().with_variant(db.Integer(), "sqlite")


def _ahora_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class RegistroAuditoria(db.Model):
    __tablename__ = "registros_auditoria"

    id = db.Column(BigId, primary_key=True, autoincrement=True)
    # Identificador del evento recibido: evita duplicados si RabbitMQ reentrega un mensaje
    evento_id = db.Column(db.String(100), nullable=False, unique=True)
    usuario_id = db.Column(db.BigInteger, index=True)
    fecha_hora = db.Column(db.DateTime, nullable=False, index=True)  # UTC
    servicio_origen = db.Column(db.String(50), nullable=False)
    tipo_operacion = db.Column(db.String(50), nullable=False, index=True)
    producto_id = db.Column(db.BigInteger, index=True)
    cantidad_anterior = db.Column(db.Integer)
    cantidad_modificada = db.Column(db.Integer)
    motivo = db.Column(db.String(255))
    referencia = db.Column(db.String(100), index=True)
    registrado_en = db.Column(db.DateTime, nullable=False, default=_ahora_utc)

    def to_dict(self):
        return {
            "id": self.id,
            "evento_id": self.evento_id,
            "usuario_id": self.usuario_id,
            "fecha_hora": iso_utc(self.fecha_hora),
            "servicio_origen": self.servicio_origen,
            "tipo_operacion": self.tipo_operacion,
            "producto_id": self.producto_id,
            "cantidad_anterior": self.cantidad_anterior,
            "cantidad_modificada": self.cantidad_modificada,
            "motivo": self.motivo,
            "referencia": self.referencia,
            "registrado_en": iso_utc(self.registrado_en),
        }


class RegistroInmutableError(RuntimeError):
    pass


@event.listens_for(RegistroAuditoria, "before_update")
@event.listens_for(RegistroAuditoria, "before_delete")
def _bloquear_cambios(mapper, connection, target):
    # Segunda barrera (la primera son los permisos MySQL: solo INSERT y SELECT)
    raise RegistroInmutableError("registros_auditoria es de solo inserción")

"""Base de lectura de ms-reportes (db_reportes). Tablas desnormalizadas y SIN llaves foráneas:
se alimentan solo con eventos, nunca se lee la BD de otro servicio (RNF02)."""
from .extensions import db
from .fechas import iso_utc

# BIGINT en MySQL; INTEGER en SQLite (para que el autoincremento funcione en las pruebas)
BigId = db.BigInteger().with_variant(db.Integer(), "sqlite")


class ProductoRM(db.Model):
    __tablename__ = "productos_rm"
    producto_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)  # id de ms-catalog
    codigo = db.Column(db.String(50), index=True)
    nombre = db.Column(db.String(200))
    precio = db.Column(db.Numeric(12, 2))
    activo = db.Column(db.Boolean, nullable=False, default=True)
    actualizado_en = db.Column(db.DateTime)


class ExistenciaRM(db.Model):
    __tablename__ = "existencias_rm"
    producto_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    bodega_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    estado = db.Column(db.String(20), index=True)  # disponible | stock_bajo | agotado
    actualizado_en = db.Column(db.DateTime)        # fecha del último evento aplicado


class MovimientoRM(db.Model):
    __tablename__ = "movimientos_rm"
    id = db.Column(BigId, primary_key=True, autoincrement=True)
    evento_id = db.Column(db.String(100), nullable=False, unique=True)  # evita contar dos veces
    movimiento_id = db.Column(db.BigInteger)
    producto_id = db.Column(db.BigInteger, nullable=False, index=True)
    bodega_id = db.Column(db.BigInteger)
    tipo = db.Column(db.String(30), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)

    __table_args__ = (db.Index("ix_mov_tipo_fecha", "tipo", "fecha"),)

    def to_dict(self):
        return {
            "producto_id": self.producto_id,
            "bodega_id": self.bodega_id,
            "tipo": self.tipo,
            "cantidad": self.cantidad,
            "fecha": iso_utc(self.fecha),
        }

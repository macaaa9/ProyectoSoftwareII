"""Consumidor RabbitMQ de ms-auditoria. Se ejecuta como proceso aparte:  python -m app.consumer

- Exchange tipo topic compartido (papiers.eventos); cola propia y durable (ms-auditoria.eventos).
- ACK manual: el mensaje se confirma solo después de guardar en BD.
- Mensajes inválidos → cola de errores <cola>.dlq.  Fallo de BD → se reencola y se reintenta.
"""
import logging
import signal
import time

import pika
from sqlalchemy.exc import SQLAlchemyError

from . import create_app
from .eventos import EventoInvalido
from .extensions import db
from .servicio import procesar_mensaje

log = logging.getLogger("consumer")


def configurar_canal(canal, cfg):
    exchange, cola = cfg["RABBITMQ_EXCHANGE"], cfg["RABBITMQ_QUEUE"]
    dlx = f"{exchange}.dlx"
    canal.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    canal.exchange_declare(exchange=dlx, exchange_type="direct", durable=True)
    canal.queue_declare(
        queue=cola,
        durable=True,
        arguments={"x-dead-letter-exchange": dlx, "x-dead-letter-routing-key": cola},
    )
    canal.queue_declare(queue=f"{cola}.dlq", durable=True)
    canal.queue_bind(queue=f"{cola}.dlq", exchange=dlx, routing_key=cola)
    for rk in cfg["RABBITMQ_ROUTING_KEYS"]:
        canal.queue_bind(queue=cola, exchange=exchange, routing_key=rk)
    canal.basic_qos(prefetch_count=cfg["RABBITMQ_PREFETCH"])


def _salir(signum, frame):
    raise SystemExit(0)


def main():
    app = create_app()
    cfg = app.config
    signal.signal(signal.SIGTERM, _salir)

    def al_recibir(canal, metodo, propiedades, cuerpo):
        with app.app_context():
            try:
                n = procesar_mensaje(cuerpo, metodo.routing_key)
                canal.basic_ack(metodo.delivery_tag)
                log.info("evento procesado", extra={"campos": {"routing_key": metodo.routing_key, "filas": n}})
            except EventoInvalido as e:
                canal.basic_nack(metodo.delivery_tag, requeue=False)
                log.warning(f"evento inválido enviado a DLQ: {e}", extra={"campos": {"routing_key": metodo.routing_key}})
            except SQLAlchemyError:
                db.session.rollback()
                log.exception("error de base de datos; se reintentará")
                time.sleep(2)
                canal.basic_nack(metodo.delivery_tag, requeue=True)

    espera = 1
    conexion = None
    try:
        while True:
            try:
                parametros = pika.URLParameters(cfg["RABBITMQ_URL"])
                parametros.heartbeat = 60
                conexion = pika.BlockingConnection(parametros)
                canal = conexion.channel()
                configurar_canal(canal, cfg)
                canal.basic_consume(queue=cfg["RABBITMQ_QUEUE"], on_message_callback=al_recibir)
                espera = 1
                log.info(
                    "escuchando eventos",
                    extra={"campos": {"cola": cfg["RABBITMQ_QUEUE"], "routing_keys": cfg["RABBITMQ_ROUTING_KEYS"]}},
                )
                canal.start_consuming()
            except pika.exceptions.AMQPError as e:
                log.warning(f"RabbitMQ no disponible ({e!r}); reintento en {espera}s")
                time.sleep(espera)
                espera = min(espera * 2, 30)
    except (SystemExit, KeyboardInterrupt):
        log.info("deteniendo consumidor")
    finally:
        if conexion is not None and conexion.is_open:
            conexion.close()


if __name__ == "__main__":
    main()

"""Publica eventos de ejemplo en RabbitMQ para probar ms-reportes (y cargar datos para pruebas de rendimiento).
    python scripts/publicar_eventos_demo.py --productos 100 --movimientos 1000
"""
import argparse
import json
import random
import uuid
from datetime import datetime, timedelta, timezone

import pika

NOMBRES = ["Cuaderno", "Lapicero", "Borrador", "Cartulina", "Carpeta", "Pintura", "Regla", "Marcador", "Colores", "Pegante"]


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def publicar(canal, exchange, rk, tipo, origen, datos, fecha):
    cuerpo = {"evento_id": str(uuid.uuid4()), "tipo": tipo, "servicio_origen": origen, "fecha": iso(fecha), "datos": datos}
    canal.basic_publish(exchange=exchange, routing_key=rk, body=json.dumps(cuerpo),
                        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2))


def estado(cantidad, minimo):
    return "agotado" if cantidad <= 0 else ("stock_bajo" if cantidad <= minimo else "disponible")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="amqp://guest:guest@localhost:5672/%2F")
    ap.add_argument("--exchange", default="papiers.eventos")
    ap.add_argument("--productos", type=int, default=50)
    ap.add_argument("--bodegas", type=int, default=2)
    ap.add_argument("--movimientos", type=int, default=500)
    a = ap.parse_args()

    conexion = pika.BlockingConnection(pika.URLParameters(a.url))
    canal = conexion.channel()
    canal.exchange_declare(exchange=a.exchange, exchange_type="topic", durable=True)

    inicio = datetime.now(timezone.utc) - timedelta(days=45)
    stock, minimos = {}, {}
    for pid in range(1, a.productos + 1):
        publicar(canal, a.exchange, "catalogo.producto.actualizado", "ProductoActualizado", "ms-catalog",
                 {"producto_id": pid, "codigo": f"P-{pid:04d}", "nombre": f"{random.choice(NOMBRES)} {pid}",
                  "precio": random.choice([800, 1200, 2500, 4500, 9900]), "activo": True}, inicio)
        for b in range(1, a.bodegas + 1):
            stock[(pid, b)], minimos[(pid, b)] = random.randint(20, 120), 10
            publicar(canal, a.exchange, "inventario.estado_stock.cambiado", "EstadoStockCambiado", "ms-inventory",
                     {"producto_id": pid, "bodega_id": b, "cantidad": stock[(pid, b)], "estado": "disponible"}, inicio)

    for i, seg in enumerate(sorted(random.uniform(0, 45 * 86400) for _ in range(a.movimientos)), 1):
        fecha = inicio + timedelta(seconds=seg)
        clave = (random.randint(1, a.productos), random.randint(1, a.bodegas))
        anterior = stock[clave]
        tipo = random.choices(["salida", "entrada", "ajuste"], weights=[7, 2, 1])[0]
        cantidad = random.randint(10, 40) if tipo == "entrada" else min(random.randint(1, 8), anterior)
        if cantidad == 0:
            continue
        nuevo = anterior + cantidad if tipo == "entrada" else anterior - cantidad
        stock[clave] = nuevo
        publicar(canal, a.exchange, "inventario.movimiento.registrado", "MovimientoRegistrado", "ms-inventory",
                 {"movimiento_id": i, "tipo": tipo, "producto_id": clave[0], "bodega_origen_id": clave[1],
                  "cantidad": cantidad, "cantidad_anterior": anterior, "cantidad_nueva": nuevo,
                  "motivo": {"salida": "Venta", "entrada": "Compra a proveedor", "ajuste": "Producto dañado"}[tipo],
                  "usuario_id": random.randint(1, 5),
                  "saldos": [{"bodega_id": clave[1], "cantidad": nuevo, "estado": estado(nuevo, minimos[clave])}]},
                 fecha)
    conexion.close()
    print(f"Publicados: {a.productos} productos, {len(stock)} existencias y ~{a.movimientos} movimientos")


if __name__ == "__main__":
    main()

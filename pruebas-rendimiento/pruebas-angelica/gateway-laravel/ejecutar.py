"""Ejecuta las 15 pruebas de rendimiento (gateway + servicios Laravel) una tras otra y escribe resultados/RESULTADOS.md.

    pip install locust
    python ejecutar.py                    # las 15, con la duración definida en cada una
    python ejecutar.py --solo P09 P10     # algunas
    python ejecutar.py --escala 0.5       # duraciones a la mitad (ensayo rápido)
    python ejecutar.py --entorno "docker compose, laptop i5 16GB"
    python ejecutar.py --sin-ejecutar     # rehace RESULTADOS.md con los CSV ya generados

Por defecto todo va al API Gateway (GATEWAY_URL=http://localhost:8000/api).
"""
import argparse
import csv
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent

# id, clase, descripción, usuarios, usuarios nuevos por segundo, duración (s), p95 máx (ms), % error máx
PRUEBAS = [
    ("P01", "P01LineaBaseGateway", "Línea base: GET /categories a través del gateway", 10, 5, 30, 300, 1),
    ("P02", "P02Login", "Login (bcrypt + emisión de JWT)", 10, 5, 30, 1000, 1),
    ("P03", "P03Usuarios", "Listado de usuarios con su rol", 20, 5, 30, 500, 1),
    ("P04", "P04ProductosPaginados", "Productos paginados", 20, 5, 30, 500, 1),
    ("P05", "P05ProductosBusqueda", "Búsqueda de productos por texto (LIKE)", 20, 5, 30, 500, 1),
    ("P06", "P06ProductoPorId", "Detalle de producto por id", 20, 5, 30, 500, 1),
    ("P07", "P07CrearProducto", "Escritura: crear producto (+ evento RabbitMQ)", 10, 5, 30, 1000, 1),
    ("P08", "P08Inventario", "Listado completo de inventario", 20, 5, 30, 800, 1),
    ("P09", "P09StockBajo", "Productos con stock bajo", 20, 5, 30, 500, 1),
    ("P10", "P10Disponibilidad", "Verificar disponibilidad de 3 productos", 20, 5, 30, 500, 1),
    ("P11", "P11Movimientos", "Escritura transaccional: movimientos de stock (+ evento)", 10, 5, 30, 1000, 1),
    ("P12", "P12Ordenes", "Listado de órdenes de compra", 20, 5, 30, 500, 1),
    ("P13", "P13CrearOrden", "Crear orden de compra (REST ms-purchase → ms-catalog)", 10, 5, 30, 1500, 1),
    ("P14", "P14CargaMixta", "Carga mixta catálogo + inventario + compras, 30 usuarios", 30, 5, 60, 1000, 1),
    ("P15", "P15Estres", "Estrés: carga mixta sin pausa, 50 usuarios", 50, 10, 30, 3000, 5),
]


def leer_agregado(prefijo):
    with open(f"{prefijo}_stats.csv", newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            if fila["Name"] == "Aggregated":
                return fila
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", nargs="*", help="ids a ejecutar, p. ej. P01 P09")
    ap.add_argument("--escala", type=float, default=1.0, help="multiplica la duración de cada prueba")
    ap.add_argument("--entorno", default=os.getenv("ENTORNO", "no especificado"),
                    help="descripción del equipo/entorno donde se corrió")
    ap.add_argument("--salida", default="resultados", help="carpeta de resultados")
    ap.add_argument("--sin-ejecutar", action="store_true", help="solo rehace el informe con los CSV existentes")
    a = ap.parse_args()

    SALIDA = AQUI / a.salida
    SALIDA.mkdir(exist_ok=True)
    destino = f"API Gateway ({os.getenv('GATEWAY_URL', 'http://localhost:8000/api')})"
    filas = []
    for pid, clase, desc, usuarios, tasa, dur, p95_max, err_max in PRUEBAS:
        if a.solo and pid not in a.solo:
            continue
        dur = max(10, int(dur * a.escala))
        prefijo = SALIDA / pid
        print(f"\n=== {pid} · {desc} · {usuarios} usuarios · {dur}s", flush=True)
        if not a.sin_ejecutar:
            subprocess.run(
                [sys.executable, "-m", "locust", "-f", str(AQUI / "locustfile.py"), clase, "--headless",
                 "-u", str(usuarios), "-r", str(tasa), "-t", f"{dur}s", "--csv", str(prefijo),
                 "--only-summary", "--loglevel", "WARNING"],
                check=False,
            )
        ag = leer_agregado(prefijo)
        if not ag or int(ag["Request Count"]) == 0:
            filas.append((pid, desc, usuarios, dur, 0, 0, 0, 0, 0, 0, 0, 100.0, p95_max, err_max, "SIN DATOS"))
            continue
        n, fallos = int(ag["Request Count"]), int(ag["Failure Count"])
        err = round(100 * fallos / n, 2)
        p95 = float(ag["95%"])
        veredicto = "CUMPLE" if p95 <= p95_max and err <= err_max else "NO CUMPLE"
        filas.append((pid, desc, usuarios, dur, n, round(float(ag["Requests/s"]), 1),
                      round(float(ag["Average Response Time"])), float(ag["50%"]), p95, float(ag["99%"]),
                      round(float(ag["Max Response Time"])), err, p95_max, err_max, veredicto))

    encabezado = ["Prueba", "Descripción", "Usuarios", "Duración (s)", "Peticiones", "Peticiones/s",
                  "Promedio (ms)", "p50 (ms)", "p95 (ms)", "p99 (ms)", "Máx (ms)", "% error",
                  "Meta p95 (ms)", "Meta % error", "Resultado"]
    with open(SALIDA / "resumen.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(encabezado)
        w.writerows(filas)

    cumplen = sum(1 for f in filas if f[-1] == "CUMPLE")
    md = [
        "# Pruebas de rendimiento · API Gateway y microservicios Laravel",
        "",
        f"- Fecha: {datetime.now():%Y-%m-%d %H:%M}",
        f"- Destino: {destino}",
        f"- Entorno: {a.entorno}",
        "- Herramienta: Locust (headless), una prueba a la vez",
        f"- Resultado: **{cumplen} de {len(filas)} pruebas cumplen su meta**",
        "",
        "| " + " | ".join(encabezado) + " |",
        "|" + "---|" * len(encabezado),
    ]
    md += ["| " + " | ".join(str(c) for c in f) + " |" for f in filas]
    md += ["", f"Detalle por endpoint: `{a.salida}/Pxx_stats.csv`; fallos: `{a.salida}/Pxx_failures.csv`."]
    (SALIDA / "RESULTADOS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
